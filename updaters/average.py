import json
import statistics
from glob import glob

from flask_sqlalchemy import SQLAlchemy

from server import Database
from util.calc import Calc
from util.runners import Runner


class AverageCalculator(Runner):
    def __init__(self, sql_db: SQLAlchemy, db: Database):
        Runner.__init__(self, self._process)
        self.sql_db = sql_db
        self.db = db

    def _get_fp(self, folder, event):
        return "clooney/{0}/{1}".format(folder, event)

    def update(self, event):
        Runner.run(self, event)

    def _process(self, event):
        print("Updating event: {}".format(event))
        from server.models import ScoutingEntry, AnalysisEntry
        entries = ScoutingEntry.query.filter_by(event=event).all()
        raw = list(map(lambda x: x.to_dict()["data"], entries))

        sorted_data = {}
        for line in raw:
            print(line)
            team = line["team"]
            if team not in sorted_data.keys():
                sorted_data[team] = {}
            for key in line:
                if key not in sorted_data[team].keys():
                    sorted_data[team][key] = []
                sorted_data[team][key].append(line[key])

        methods = json.load(open(self._get_fp('analysis', event) + ".json"))

        from server.models import Event
        teams = list(map(lambda x: x["team_number"], Event.query.filter_by(id=event).first().get_team_list()))
        for team_number, team_data in sorted_data.items():
            if team_number not in teams:
                print("Error entry for team {0}: {1}".format(team_number, team_data))
                continue
            avg = {}
            for field in methods:
                key = field["key"]
                if key in team_data:
                    avg[key] = {}
                    avg[key]['raw'] = team_data[key]
                    if field["method"] == "count":
                        avg[key]["value"] = len(team_data[key])
                    elif field["method"] == "count_true":
                        avg[key]["value"] = team_data[key].count(True)
                    elif field["method"] == "sum":
                        avg[key]["value"] = sum(map(float, team_data[key]))
                    elif field["method"] == "avg":
                        avg[key]["value"] = round(statistics.mean(map(float, team_data[key])), 2)
                        avg[key]["med_grp"] = round(statistics.median_grouped(map(float, team_data[key])), 2)
                        avg[key]["std_dev"] = round(statistics.pstdev(map(float, team_data[key])), 2)
                    elif field["method"] == "percent":
                        avg[key]["mean"] = statistics.mean(map(lambda x: float(x), team_data[key]))
                        avg[key]["value"] = int(avg[key]["mean"] * 100)
                        avg[key]["percent"] = "{}%".format(avg[key]["value"])
                    elif field["method"] == "mode":
                        mode = self._calc_mode(team_data[key])
                        count_mode = team_data[key].count(mode)
                        avg[key]["value"] = mode
                        avg[key]["count_common"] = "{0} [{1}]".format(mode, count_mode)
                        avg[key]["percent_common"] = "{0} {1}%".format(mode, str(int(100*count_mode/len(team_data[key]))).zfill(3))
                        avg[key]["common_percent"] = int(100*count_mode/len(team_data[key]))
                    elif field["method"] == "avg_col":
                        counts = {}
                        for entry in team_data[key]:
                            for option in entry.keys():
                                if option not in counts.keys():
                                    counts[option] = 0
                                if "2" in entry[option]:
                                    counts[option] += 2
                                elif "1" in entry[option]:
                                    counts[option] += 1
                        avg[key]["value"] = round(sum(map(lambda x: x[1], counts.items())) / len(team_data[key]), 2)
                        avg[key]["counts"] = counts
            entry_id = "{0}_{1}_{2}".format(event, "avg", team_number)
            entry = AnalysisEntry.query.filter_by(id=entry_id).first()
            if entry:
                entry.data = json.dumps(avg)
            else:
                avg_entry = AnalysisEntry(entry_id, event, int(team_number), avg, "avg")
                self.sql_db.session.add(avg_entry)
        self.sql_db.session.commit()
        self._calculate_expressions(event)
        print("Done")

    def _calculate_expressions(self, event):
        print("Updating Expressions: {}".format(event))
        from server.models import AnalysisEntry
        calculator = Calc()
        entries = AnalysisEntry.query.filter_by(event=event, key="avg").all()
        oprs = self.db.get_event_oprs(event)
        if entries:
            avg_data = list(map(lambda x: x.to_dict()["data"], entries))
            expressions = json.load(open(self._get_fp('expressions', event) + ".json"))
            for team in avg_data:
                team_number = team['team']["value"]
                calculator.add_fields(avg=team)
                if team_number not in oprs.keys():
                    continue
                calculator.add_fields(opr=oprs[team_number])
                team_calc = {}
                for expression in expressions:
                    calculator.add_fields(calculated=team_calc)
                    eq = expression["expression"]
                    try:
                        val = calculator.solve(eq)
                        if "round" in expression.keys():
                            val = round(val, int(expression["round"]))
                        team_calc[expression["key"]] = val
                    except Exception as ex:
                        print(eq)
                        raise ex
                    team['calculated'] = team_calc
                entry_id = "{0}_{1}_{2}".format(event, "calc", team_number)
                entry = AnalysisEntry.query.filter_by(id=entry_id).first()
                if entry:
                    entry.set_data(team_calc)
                else:
                    calc_entry = AnalysisEntry(entry_id, event, int(team_number), team_calc, "calc")
                    self.sql_db.session.add(calc_entry)
            self.sql_db.session.commit()

    def _calc_mode(self, data):
        freq = {}
        for entry in data:
            if entry:
                if entry not in freq.keys():
                    freq[entry] = 0
                freq[entry] += 1
        return sorted(list(freq.items()), key=lambda x: x[1])[-1][0] if len(freq) > 0 else ''

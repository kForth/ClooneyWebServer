import json
import statistics
from glob import glob

from flask_sqlalchemy import SQLAlchemy

from util.calc import Calc
from util.runners import Runner
from server.db import Database


class AverageCalculator(Runner):
    def __init__(self, db: Database, sql_db: SQLAlchemy):
        Runner.__init__(self, self._process)
        self.db = db
        self.sql_db = sql_db

    def _get_fp(self, folder, event):
        return "../clooney/{0}/{1}".format(folder, event)

    def update(self, event):
        Runner.run(self, event)

    def _process(self, event=None):
        if event is None:
            return
        from server.models import ScoutingEntry, AnalysisEntry
        entries = ScoutingEntry.query.filter_by(event=event).all()
        raw = list(map(lambda x: x.to_dict()["data"], entries))

        # raw = []
        # try:
        #     data = json.load(open(self._get_fp('data', event) + "/raw_data.json"))
        #     if type(data) is list:
        #         raw = sorted(data, key=lambda x: x["team_number"])
        # except Exception as ex:
        #     print(ex)
        #     return

        sorted_data = {}
        for line in raw:
            team = dict(line)["team_number"]
            if team not in sorted_data.keys():
                sorted_data[team] = {}
            for key in line:
                if key not in sorted_data[team].keys():
                    sorted_data[team][key] = []
                sorted_data[team][key].append(line[key])

        methods = json.load(open(self._get_fp('analysis', event) + ".json"))
        avg_data = []
        for team_number, team_data in sorted_data.items():
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
                        avg[key]["mean"] = statistics.mean(map(float, team_data[key]))
                        avg[key]["value"] = int(avg[key]["mean"] * 100)
                        avg[key]["percent"] = "{}%".format(avg[key]["value"])
                    elif field["method"] == "mode":
                        mode = self.calc_mode(team_data[key])
                        avg[key]["value"] = mode
                        avg[key]["count_common"] = "{0} [{1}]".format(mode, team_data[key].count(mode))
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
            # avg_data.append(avg)
            entry_id = "{0}_{1}_{2}".format(event, "avg", team_number)
            entry = AnalysisEntry.query.filter_by(id=entry_id).first()
            if entry:
                entry.data = json.dumps(avg)
            else:
                avg_entry = AnalysisEntry(entry_id, event, int(team_number), avg, "avg")
                self.sql_db.session.add(avg_entry)
        self.sql_db.session.commit()
        self.save_data(event, avg_data)

    def calculate_expressions(self, event):
        from server.models import AnalysisEntry
        calculator = Calc()
        files = glob(self._get_fp('expressions', "*.json"))
        events = map(lambda x: ".".join(x.split("/")[-1].split(".")[:-1]), files)
        if event in events:
            entries = AnalysisEntry.query.filter_by(event=event, key="avg").all()
            avg_data = list(map(lambda x: x.to_dict()["data"], entries))
            # json.load(open(self._get_fp('data', event) + "/avg_data.json"))
            expressions = json.load(open(self._get_fp('expressions', event) + ".json"))
            for team in avg_data:
                team_number = team['team_number']["value"]
                calculator.add_fields(avg=team)
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
                entry = AnalysisEntry.query.filter_by(id=entry_id)
                if entry:
                    entry.data = json.dumps(team_calc)
                else:
                    calc_entry = AnalysisEntry(entry_id, event, int(team_number), team_calc, "calc")
                    self.sql_db.session.add(calc_entry)
            self.sql_db.session.commit()
            json.dump(avg_data, open(self._get_fp('data', event) + "/avg_data.json", "w+"))

    def calc_mode(self, data):
        freq = {}
        for entry in data:
            if entry not in freq.keys():
                freq[entry] = 0
            freq[entry] += 1
        return sorted(freq.items(), key=lambda x: x[1])[-1][0]

    def save_data(self, event, data):
        json.dump(data, open(self._get_fp('data', event) + "/avg_data.json", "w+"))
        self.calculate_expressions(event)


if __name__ == "__main__":
    from server import sql_db
    db = Database(path_prefix="../")
    ac = AverageCalculator(db, sql_db)
    ac.update("2017onto2")

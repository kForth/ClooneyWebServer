import json
import statistics
from glob import glob

from util.calc import Calc
from util.runners import Runner


class AverageCalculator(Runner):
    def __init__(self):
        Runner.__init__(self, self._process)

    def _get_fp(self, folder, event):
        return "../clooney/{0}/{1}".format(folder, event)

    def update(self, event):
        Runner.run(self, event)

    def _process(self, event=None):
        if event is None:
            return
        raw = []
        try:
            data = json.load(open(self._get_fp('data', event) + "/raw_data.json"))
            if type(data) is list:
                raw = sorted(data, key=lambda x: x["team_number"])
        except Exception as ex:
            print(ex)
            return

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
                        avg[key]["value"] = str(int(avg[key]["mean"] * 100))
                    elif field["method"] == "mode":
                        avg[key]["value"] = self.calc_mode(team_data[key])
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
            avg_data.append(avg)

        self.save_data(event, avg_data)

    def calculate_expressions(self, event):
        calculator = Calc()
        files = glob(self._get_fp('expressions', "*.json"))
        events = map(lambda x: ".".join(x.split("/")[-1].split(".")[:-1]), files)
        if event in events:
            avg_data = json.load(open(self._get_fp('data', event) + "/avg_data.json"))
            expressions = json.load(open(self._get_fp('expressions', event) + ".json"))
            calculated = dict(zip([x['team_number']['value'] for x in avg_data], [dict({})] * len(avg_data)))
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
            json.dump(avg_data, open(self._get_fp('data', event) + "/avg_data.json", "w+"))

            # calc = Calculator()
            # files = glob("clooney/expressions/*.json")
            # events = map(lambda x: ".".join(x.split("/")[-1].split(".")[:-1]), files)
            # if event in events:
            #     avg_data = json.load(open(self.fp + "/avg_data.json".format(event)))
            #     expressions = json.load(open("clooney/expressions/{}.json".format(event)))
            #     for team in avg_data:
            #         team["calculated"] = {}
            #         for expression in expressions:
            #             eq = expression["expression"]
            #             new_eq = ""
            #             for seg in re.split('\[|\]', eq):
            #                 if any([key in seg for key in team.keys()]):
            #                     val = team
            #                     for key in seg.replace(" ", "").split(","):
            #                         val = val[key]
            #                     if type(val) is str and "%" in val:
            #                         val = float(val.replace("%", "")) / 100
            #                     new_eq += str(val)
            #                 else:
            #                     new_eq += seg
            #             team["calculated"][expression["key"]] = calc.solve(new_eq)
            #     json.dump(avg_data, open(self.fp + "/avg_data.json".format(event), "w+"))

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
    ac = AverageCalculator()
    ac.update("2016cur")

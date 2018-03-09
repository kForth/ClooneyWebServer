import json
from os import path


class Database(object):
    def __init__(self, dirpath="db/", path_prefix=""):
        self.folder_path = dirpath
        self.path_prefix = path_prefix

        self.event_info_fp = "events.json"
        self.opr_fp = "oprs.json"

    def _load_file(self, filename: str, default="{}"):
        fp = self.path_prefix + self.folder_path + filename
        self._check_file(fp, default)
        return json.load(open(fp, 'r'))

    def _dump_file(self, data, filename: str):
        fp = self.path_prefix + self.folder_path + filename
        json.dump(data, open(fp, 'w+'))

    def __get_file(self, fp):
        if not path.isfile(self.path_prefix + fp):
            return []
        return json.load(open(self.path_prefix + fp))

    def _check_file(self, fp, default):
        if not path.isfile(self.path_prefix + fp):
            open(self.path_prefix + fp, "w+").write(default)

    def add_scouting_entry(self, event: str, entry: dict):
        fp = "event/{}/raw.json".format(event)
        data = self._load_file(fp, default="[]")
        data.append(entry)
        self._dump_file(data, fp)

    def get_event_info(self, event_id: str):
        events = self.get_events()
        return events[event_id] if event_id in events.keys() else {}

    def set_event_info(self, event_id: str, info: dict):
        events = self.get_events()
        events[event_id] = info
        self._set_events(events)

    def get_events(self):
        return self._load_file(self.event_info_fp)

    def _set_events(self, data: list):
        self._dump_file(data, self.event_info_fp)

    def add_event(self, key: str, info: dict):
        d = self.get_events()
        if key not in d.keys():
            d[key] = info
        self._set_events(d)

    def get_event_oprs(self, event_id):
        from server.models import OprEntry
        entries = OprEntry.query.filter_by(event=event_id).all()
        data = {}
        for entry in entries:
            if entry.team not in data.keys():
                data[entry.team] = {}
            if entry.score_key not in data[entry.team].keys():
                data[entry.team][entry.score_key] = entry.value
        return data

    def set_event_oprs(self, event_id, opr_dict):
        oprs = self._load_file(self.opr_fp)
        oprs[event_id] = opr_dict
        self._dump_file(oprs, self.opr_fp)

    def get_table_headers(self, event, key):
        file_path = 'clooney/headers/{}.json'.format(event)
        headers = json.load(open(file_path))
        if key not in headers.keys():
            return []
        else:
            for i in range(len(headers[key])):
                headers[key][i]['sort_id'] = chr(ord('a') + i)
            return headers[key]

    def get_raw_data(self, event_id):
        from server.models import ScoutingEntry
        entries = ScoutingEntry.query.filter_by(event=event_id).all()
        return [elem.to_dict()["data"] for elem in entries]

    def get_stats(self, event_id):
        from server.models import AnalysisEntry
        entries = AnalysisEntry.query.filter_by(event=event_id, key="avg").all()
        oprs = self.get_event_oprs(event_id)
        calc = AnalysisEntry.query.filter_by(event=event_id, key="calc").all()
        calc = dict(zip(map(lambda x: x.team, calc), map(lambda x: x.get_data(), calc)))
        for entry in entries:
            data = entry.get_data()
            team_number = data["team"]["value"]
            if team_number in oprs.keys():
                opr_dict = oprs[team_number]
                data["opr"] = dict(zip(opr_dict.keys(), map(lambda x: round(x, 1), opr_dict.values())))
                if team_number in calc.keys():
                    data["calc"] = calc[team_number]
            entry.set_data(data)
        return dict([(str(elem.team), elem.get_data()) for elem in entries])

    def get_avg_data(self, event_id):
        from server.models import AnalysisEntry
        entries = AnalysisEntry.query.filter_by(event=event_id, key="avg").all()
        return dict([(str(elem.team), elem.get_data()) for elem in entries])

    def get_calculated_data(self, event_id):
        from server.models import AnalysisEntry
        entries = AnalysisEntry.query.filter_by(event=event_id, key="calc").all()
        return dict([(str(elem.team), elem.get_data()) for elem in entries])

    def get_pit_scouting(self, event_id):
        from server.models import AnalysisEntry
        entries = AnalysisEntry.query.filter_by(event=event_id, key="pit").all()
        return dict([(str(elem.team), elem.get_data()) for elem in entries])

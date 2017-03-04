import json
from os import path


class Database(object):
    def __init__(self, dirpath="db/"):
        self.folder_path = dirpath

        self.event_info_fp = "events.json"
        self.opr_fp = "oprs.json"

    def _load_file(self, filename: str, default="{}"):
        fp = self.folder_path + filename
        self._check_file(fp, default)
        return json.load(open(fp, 'r'))

    def _dump_file(self, data, filename: str):
        fp = self.folder_path + filename
        json.dump(data, open(fp, 'w+'))

    @staticmethod
    def _check_file(fp, default):
        if not path.isfile(fp):
            open(fp, "w+").write(default)

    def add_scouting_entry(self, event: str, entry: dict):
        fp = "event/{}/raw.json".format(event)
        data = self._load_file(fp, default="[]")
        data.append(entry)
        self._dump_file(data, fp)

    def get_event_info(self, event_id: str):
        events = self._get_events()
        return events[event_id] if event_id in events.keys() else {}

    def set_event_info(self, event_id: str, info: dict):
        events = self._get_events()
        events[event_id] = info
        self._set_events(events)

    def _get_events(self):
        return self._load_file(self.event_info_fp)

    def _set_events(self, data: list):
        self._dump_file(data, self.event_info_fp)

    def add_event(self, key: str, info: dict):
        d = self._get_events()
        if key not in d.keys():
            d[key] = info
        self._set_events(d)

    def get_event_oprs(self, event_id):
        oprs = self._load_file(self.opr_fp)
        if event_id in oprs:
            return oprs[event_id]
        else:
            return {}

    def set_event_oprs(self, event_id, opr_dict):
        oprs = self._load_file(self.opr_fp)
        oprs[event_id] = opr_dict
        self._dump_file(oprs, self.opr_fp)

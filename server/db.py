import json
from os import path


class Database(object):
    def __init__(self):
        self.folder_path = "db/"

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
        return self.get_events()[event_id]

    def set_event_info(self, event_id: str, info: dict):
        events = self.get_events()
        events[event_id] = info
        self.set_events(events)

    def get_events(self):
        return self._load_file("events.json")

    def set_events(self, data: list):
        self._dump_file(data, "events.json")

    def add_event(self, key: str, info: dict):
        d = self.get_events()
        if key not in d.keys():
            d[key] = info
        self.set_events(d)

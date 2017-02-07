import json
from os import path


class Database(object):
    def __init__(self):
        self.folder_path = "db"

    def _load_file(self, filename, default="{}"):
        fp = self.folder_path + filename
        self._check_file(fp, default)
        return json.load(open(fp, 'r'))

    def _dump_file(self, data, filename):
        fp = self.folder_path + filename
        json.dump(data, open(fp, 'w+'))

    def _check_file(self, fp, default):
        if not path.isfile(fp):
            open(fp, "w+").write(default)

    def add_scouting_entry(self, event, entry):
        fp = "/event/{}/raw.json".format(event)
        data = self._load_file(fp, default="[]")
        data.append(entry)
        self._dump_file(data, fp)

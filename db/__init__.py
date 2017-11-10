import json
from os import path


class DatabaseInteractor:
    def __init__(self, folder_path, filename="db.json"):
        self.filepath = folder_path + ("" if folder_path[-1] == "/" else "/") + filename
        self._db = self._load_db()

    def _load_db(self):
        if path.isfile(self.filepath):
            return json.load(open(self.filepath))
        else:
            open(self.filepath, "w+").write("{}")
            return self._load_db()

    def _commit_db(self):
        json.dump(self._db, open(self.filepath, "w+"))

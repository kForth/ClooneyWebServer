import json
from os import path

from db.tba import TbaInteractor


class DatabaseInteractor:
    DEFAULT_DB = {'events': {}, 'users': {}}

    def __init__(self, folder_path, filename="db.json"):
        self.filepath = folder_path + ("" if folder_path[-1] == "/" else "/") + filename
        self._db = self._load_db()
        self._tba = TbaInteractor(self)

    def _load_db(self):
        if path.isfile(self.filepath):
            return json.load(open(self.filepath))
        else:
            json.dump(self.DEFAULT_DB, open(self.filepath, "w+"))
            return self._load_db()

    def _commit_db(self):
        json.dump(self._db, open(self.filepath, "w+"))

    def setup_event(self, key):
        self._db['events'][key] = {
            'tba': {},
            'matches': {},
            'teams': []
        }
        self._tba.update_event_details(key)

        self._commit_db()

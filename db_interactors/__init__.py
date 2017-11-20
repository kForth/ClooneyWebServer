import json
from os import path

from db_interactors.entry import EntryDatabaseInteractor
from db_interactors.event import EventDatabaseInteractor
from db_interactors.sheet import SheetDatabaseInteractor
from db_interactors.user import UserDatabaseInteractor


class DatabaseInteractor:
    DEFAULT_DB = {
        'events': {}, 'users': {'users': [], 'max_id': -1}, 'sheets': [], 'entry': {'entry': [], 'max_id': -1}
    }

    def __init__(self, app, filename="db/db.json"):
        self._filepath = app.root_path + "/" + filename
        self._app = app
        self._read_db()

        self.users = UserDatabaseInteractor(self, app)
        self.sheets = SheetDatabaseInteractor(self, app)
        self.events = EventDatabaseInteractor(self, app)
        self.entries = EntryDatabaseInteractor(self)

    def _read_db(self):
        self.db = self.DEFAULT_DB
        if path.isfile(self._filepath):
            self.db.update(json.load(open(self._filepath)))
        self.commit()

    def commit(self):
        json.dump(self.db, open(self._filepath, "w+"))

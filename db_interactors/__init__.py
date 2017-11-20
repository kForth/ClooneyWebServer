import json
from os import path

from db_interactors.entry import EntryDatabaseInteractor
from db_interactors.event import EventDatabaseInteractor
from db_interactors.sheet import SheetDatabaseInteractor
from db_interactors.tba import TbaInteractor
from db_interactors.user import UserDatabaseInteractor


class DatabaseInteractor:
    DEFAULT_DB = {
        'events': {}, 'users': {'users': [], 'max_id': -1}, 'sheets': [], 'entry': {'entry': [], 'max_id': -1}
    }

    def __init__(self, app, filename="db/db.json"):
        self._filepath = app.root_path + "/" + filename
        self._app = app
        self._read_db()

        self.tba_interactor = TbaInteractor(self, app)
        self.user_interactor = UserDatabaseInteractor(self, app)
        self.sheet_interactor = SheetDatabaseInteractor(self, app)
        self.event_interactor = EventDatabaseInteractor(self)
        self.entry_interactor = EntryDatabaseInteractor(self)

    def _read_db(self):
        if path.isfile(self._filepath):
            self.db = self.DEFAULT_DB.update(json.load(open(self._filepath)))
        else:
            self.db = self.DEFAULT_DB
            self.commit()

    def commit(self):
        json.dump(self.db, open(self._filepath, "w+"))

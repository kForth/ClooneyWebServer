import json
from os import path

from db_interactors.calculator import CalculatorDatabaseInteractor
from db_interactors.entry import EntryDatabaseInteractor
from db_interactors.event import EventDatabaseInteractor
from db_interactors.sheet import SheetDatabaseInteractor
from db_interactors.user import UserDatabaseInteractor
from util import PeriodicRunner


class DatabaseInteractor:
    DEFAULT_DB = {
        'user_event_headers': {}, 'calculations': {'analysis': {}, 'calculations': {}}, 'event_settings': {}, 'events': {}, 'user_settings': {}, 'users': {'users': [], 'max_id': -1}, 'sheets': {'sheets': [], 'max_id': -1}, 'entry': {'entry': [], 'max_id': -1}
    }

    def __init__(self, app, filename="db/db.json"):
        self._filepath = app.root_path + "/" + filename
        self._app = app
        self._read_db()

        self.commit_runner = PeriodicRunner(target=self.commit, delay=60)

        self.users = UserDatabaseInteractor(self, app)
        self.sheets = SheetDatabaseInteractor(self, app)
        self.events = EventDatabaseInteractor(self, app)
        self.entries = EntryDatabaseInteractor(self)
        self.calculator = CalculatorDatabaseInteractor(self)

    def _read_db(self):
        self.db = self.DEFAULT_DB
        if path.isfile(self._filepath):
            try:
                self.db.update(json.load(open(self._filepath)))
            except:
                self.db.update(json.load(open(self._filepath + ".backup")))
        self.commit()

    def commit(self):
        json.dump(self.db, open(self._filepath, "w+"))

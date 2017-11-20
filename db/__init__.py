import json
from os import path

from db.api.event_api import EventDatabaseEndpoints
from db.api.sheet_api import SheetDatabaseEndpoints
from db.api.user_api import UserDatabaseEndpoints
from db.interactors.event import EventDatabaseInteractor
from db.interactors.sheet import SheetDatabaseInteractor
from db.interactors.tba import TbaInteractor
from db.interactors.user import UserDatabaseInteractor


class DatabaseInteractor:
    DEFAULT_DB = {'events': {}, 'users': {'users': [], 'max_id': -1}, 'sheets': []}

    def __init__(self, app, filename="db.json"):
        self._filepath = app.root_path + "/" + filename
        self._app = app
        self.db = self._read()

        self._user_interactor = UserDatabaseInteractor(self, self._app)
        self._user_endpoints = UserDatabaseEndpoints(self._user_interactor, self._app)

        self._sheet_interactor = SheetDatabaseInteractor(self, self._app)
        self._sheet_endpoints = SheetDatabaseEndpoints(self._sheet_interactor, self._app)

        self._tba_interactor = TbaInteractor(self, self._app)
        # self._tba_endpoints = TbaDatabaseEndpoints(self._tba_interactor, self._app)

        self._event_interactor = EventDatabaseInteractor(self, self._app)
        self._event_endpoints = EventDatabaseEndpoints(self._event_interactor, self._app)

    def get_users(self):
        return self.db['users']

    def _read(self):
        if path.isfile(self._filepath):
            return json.load(open(self._filepath))
        else:
            json.dump(self.DEFAULT_DB, open(self._filepath, "w+"))
            return self._read()

    def commit(self):
        json.dump(self.db, open(self._filepath, "w+"))

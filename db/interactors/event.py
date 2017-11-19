class EventDatabaseInteractor:
    def __init__(self, db, app):
        self._db = db
        self._app = app

    def get_events(self):
        return list(map(lambda x: x['info']['data'], self._db.db['events'].values()))

    def get_event(self, key):
        return dict(self._db.db['events'][key])

    def set_event(self, key, data):
        self._db.db['events'][key] = data
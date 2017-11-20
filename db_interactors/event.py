class EventDatabaseInteractor:
    def __init__(self, db):
        self._db = db

    def get_events(self):
        return list(map(lambda x: x['info'], self._db.db['events'].values()))

    def get_event(self, key):
        return dict(self._db.db['events'][key])

    def set_event(self, key, data):
        self._db.db['events'][key] = data
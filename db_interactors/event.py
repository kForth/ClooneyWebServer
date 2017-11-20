from tba_py import TBA


class EventDatabaseInteractor:
    def __init__(self, db, app):
        self._db = db
        self._tba = TBA(app.config['TBA_AUTH_KEY'], cache_filename=app.config['TBA_CACHE_FILE'])

    def get_event_keys(self):
        return self._db.db['events'].keys()

    def get_events(self):
        return list(map(lambda x: x['info']['data'], self._db.db['events'].values()))

    def get_event(self, key):
        return dict(self._db.db['events'][key])

    def set_event(self, key, data):
        self._db.db['events'][key] = data
        self._db.commit()

    def get_search_events(self):
        events = []
        events += self._tba.get_events_simple(2018)
        events += self._tba.get_events_simple(2017)
        return events

    def update_event_details(self, key):
        event = self.get_event(key)
        event['info']['data'] = self._tba.get_event_info(key)
        event['info']['data']['is_tba'] = True
        self.set_event(key, event)
        self._db.commit()

    def update_event_teams(self, key):
        event = self.get_event(key)
        event['info']['teams'] = self._tba.get_event_teams(key)
        self.set_event(key, event)
        self._db.commit()

    def update_event_matches(self, key):
        event = self.get_event(key)
        event['info']['matches'] = self._tba.get_event_matches(key)
        self.set_event(key, event)
        self._db.commit()

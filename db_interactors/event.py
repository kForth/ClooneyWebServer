from models import Event
from tba_py import TBA


class EventDatabaseInteractor:
    def __init__(self, db, app):
        self._db = db
        self._tba = TBA(app.config['TBA_AUTH_KEY'], cache_filename=app.config['TBA_CACHE_FILE'])

    def get_event_settings(self, key):
        return self._db.db['event_settings'][key]

    def set_event_settings(self, key, settings):
        self._db.db['event_settings'][key] = settings

    def get_events(self):
        return [Event.from_json(e) for e in self._db.db['events'].values()]

    def get_event_keys(self):
        return [e.key for e in self.get_events()]

    def get_events_data(self):
        return list(map(lambda x: x.info.data, self.get_events()))

    def get_event(self, key):
        events = [e for e in self.get_events() if e.key == key]
        return events[0] if events else None

    def set_event(self, key, data):
        self._db.db['events'][key] = data.to_dict()

    def get_search_events(self):
        events = []
        events += self._tba.get_events_simple(2018)
        events += self._tba.get_events_simple(2017)
        return events

    def update_event_details(self, key):
        event = self.get_event(key)
        event.info.data = self._tba.get_event_info(key)
        event.info.is_tba = True
        self.set_event(key, event)

    def update_event_teams(self, key):
        event = self.get_event(key)
        event.teams = self._tba.get_event_teams(key)
        self.set_event(key, event)

    def update_event_matches(self, key):
        event = self.get_event(key)
        event.matches = self._tba.get_event_matches(key)
        self.set_event(key, event)

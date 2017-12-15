from models import Event
from tba_py import TBA


class EventDatabaseInteractor:
    DEFAULT_EVENT_SETTINGS = {'settings': {'selected_sheet': {}}, 'calculations': []}

    def __init__(self, db, app):
        self._db = db
        self._tba = TBA(app.config['TBA_AUTH_KEY'], cache_filename=app.config['TBA_CACHE_FILE'])

    def get_event_settings(self, key):
        return self._db.db['event_settings'][key]

    def set_event_settings(self, key, settings=DEFAULT_EVENT_SETTINGS):
        if key not in self._db.db['event_settings'].keys():
            self._db.db['event_settings'][key] = {}
        self._db.db['event_settings'][key].update(settings)

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



    def update_event_headers_by_user_id(self, user_id, event_key, data):
        if user_id not in self._db.db['user_event_headers'].keys():
            self._db.db['user_event_headers'][user_id] = {}
        if event_key not in self._db.db['user_event_headers'][user_id].keys():
            self._db.db['user_event_headers'][user_id][event_key] = {}
        self._db.db['user_event_headers'][user_id][event_key].update(data)

    def get_default_event_headers(self, event_key):
        if 'default' in self._db.db['user_event_headers'].keys() and event_key in self._db.db['user_event_headers']['default'].keys():
            return self._db.db['user_event_headers']['default'][event_key]
        return self.update_default_event_headers(event_key)

    def update_default_event_headers(self, event_key):
        headers = {
            '/a/a': [],
            '/a/e': []
        }
        event_sheet = json.loads(self._db.db['event_settings'][event_key]['selected_sheet'])['data']
        if event_sheet:
            raw_headers = [
                {
                    "data_key":   "match",
                    "class":      "",
                    "title":      "M#",
                    "data_class": "",
                    "tooltip":    ""
                },
                {
                    "data_key":   "pos",
                    "class":      "",
                    "title":      "P#",
                    "data_class": "",
                    "tooltip":    ""
                },
                {
                    "data_key":   "team",
                    "class":      "",
                    "title":      "Team",
                    "data_class": "",
                    "tooltip":    ""
                },
            ]
            avg_headers = [dict(e) for e in raw_headers]
            del avg_headers[1]
            avg_headers[0]['data_key'] += '.count'
            avg_headers[1]['data_key'] += '.mode'
            for line in event_sheet:
                if line['type'] in ['Image', 'Divider']:
                    continue
                header = {
                    "data_key":   line['key'],
                    "class":      "",
                    "title":      line['label'],
                    "data_class": "",
                    "tooltip":    ""
                }
                raw_headers.append(dict(header))
                if line['type'] == 'Numbers':
                    header["data_key"] += ".avg"
                elif line['type'] == 'Boolean':
                    header["data_key"] += ".mode"
                elif line['type'] == 'HorizontalOptions':
                    header["data_key"] += ".mode"
                avg_headers.append(header)

            headers['/a/e'] = raw_headers
            headers['/a/a'] = avg_headers

            if 'default' not in self._db.db['user_event_headers'].keys():
                self._db.db['user_event_headers']['default'] = {}
            self._db.db['user_event_headers']['default'][event_key] = headers

        return headers

    def get_event_headers_by_user_id(self, user_id, event_key):
        if user_id in self._db.db['user_event_headers'].keys():
            if event_key in self._db.db['user_event_headers'][user_id].keys():
                headers = self._db.db['user_event_headers'][event_key]
                return headers if headers else self.get_default_event_headers(event_key)
        return {}

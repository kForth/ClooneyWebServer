import json

from models import Event
from tba_py import TBA


class EventDatabaseInteractor:
    DEFAULT_EVENT_SETTINGS = {
        'settings':     {
            'selected_sheet':           {},
            'default_avg_headers':      {},
            'default_raw_headers':      {},
            'default_team_raw_headers': {}
        },
        'calculations': []
    }

    def __init__(self, db, app):
        self._db = db
        self._tba = TBA(app.config['TBA_AUTH_KEY'], cache_filename=app.config['TBA_CACHE_FILE'])

        if 'events' not in self._db.db.keys():
            self._db.db['events'] = {}
        if 'event_settings' not in self._db.db.keys():
            self._db.db['event_settings'] = {}
        if 'user_event_headers' not in self._db.db.keys():
            self._db.db['user_event_headers'] = {}

    def get_event_settings(self, key):
        settings = dict(self.DEFAULT_EVENT_SETTINGS.items())
        settings.update(self._db.db['event_settings'][key])
        return settings

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
        event.matches = []
        for match in self._tba.get_event_matches(key):
            match['alliances']['red']['team_keys'] = [e.strip('frc') for e in match['alliances']['red']['team_keys']]
            match['alliances']['blue']['team_keys'] = [e.strip('frc') for e in match['alliances']['blue']['team_keys']]
            match['short_key'] = match['key'].split('_')[-1]
            event.matches += [match]
        self.set_event(key, event)

    def get_default_event_headers(self, event_key):
        if 'default' in self._db.db['user_event_headers'].keys() and \
                        event_key in self._db.db['user_event_headers']['default'].keys():
            return self._db.db['user_event_headers']['default'][event_key]
        else:
            headers = self.get_auto_generated_headers(event_key)
            self.set_default_event_headers(event_key, headers)
            return headers

    def set_default_event_headers(self, event_key, headers, update=True):
        print(headers)
        if 'default' not in self._db.db['user_event_headers'].keys():
            self._db.db['user_event_headers']['default'] = {}
        if update:
            self._db.db['user_event_headers']['default'][event_key].update(headers)
        else:
            self._db.db['user_event_headers']['default'][event_key] = headers
        print(self._db.db['user_event_headers']['default'][event_key])

    def get_user_event_headers(self, user_id, event_key):
        headers = self.get_default_event_headers(event_key)
        if user_id in self._db.db['user_event_headers'].keys():
            if event_key in self._db.db['user_event_headers'][user_id].keys():
                headers.update(self._db.db['user_event_headers'][event_key])
        return headers

    def set_user_default_event_headers(self, user_id, event_key, data, update=True):
        if user_id not in self._db.db['user_event_headers'].keys():
            self._db.db['user_event_headers'][user_id] = {}
        if event_key not in self._db.db['user_event_headers'][user_id].keys():
            self._db.db['user_event_headers'][user_id][event_key] = {}
        if update:
            self._db.db['user_event_headers'][user_id][event_key].update(data)
        else:
            self._db.db['user_event_headers'][user_id][event_key] = data

    def get_auto_generated_headers(self, event_key, pages=('/a/a', '/a/e', '/a/t/e')):
        headers = dict([(e, []) for e in pages])
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
            team_raw_headers = [dict(e) for e in raw_headers[:1]]
            avg_headers = [dict(e) for e in raw_headers]
            del avg_headers[1]
            avg_headers[0]['data_key'] += '.count'
            avg_headers[1]['data_key'] += '.mode'
            for line in event_sheet:
                if line['type'] in ['Image', 'Divider']:
                    continue
                header = {
                    "data_key": line['key'],
                    "class":        "",
                    "title": line   ['label'],
                    "data_class":   "",
                    "tooltip":      ""
                }
                if '/a/e' in pages:
                    raw_headers.append(dict(header))
                if '/a/t/e' in pages:
                    team_raw_headers.append(dict(header))
                if '/a/a' in pages:
                    if line['type'] == 'Numbers':
                        header["data_key"] += ".avg"
                    elif line['type'] == 'Boolean':
                        header["data_key"] += ".mode"
                    elif line['type'] == 'HorizontalOptions':
                        header["data_key"] += ".mode"
                    avg_headers.append(header)

            if '/a/e' in pages:
                headers['/a/e'] = raw_headers
            if '/a/t/e' in pages:
                headers['/a/t/e'] = team_raw_headers
            if '/a/a' in pages:
                headers['/a/a'] = avg_headers

        return headers

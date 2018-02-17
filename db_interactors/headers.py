import json
import random

from models import HeaderGroup


class HeadersDatabaseInteractor:
    def __init__(self, db):
        self._db = db

        if 'headers' not in self._db.db.keys():
            self._db.db['headers'] = {}
            self._db.commit()

    def get_header_groups(self):
        return [HeaderGroup.from_json(e) for e in self._db.db['headers'].values()]

    def get_header_group(self, group_id):
        return HeaderGroup.from_json(self._db.db['headers'][str(group_id)])

    def create_header_group(self, creator_id, path):
        return HeaderGroup('New Group', creator_id, path, [], self.get_next_group_id())

    def set_header_group(self, group, update=True):
        self.set_header_groups([group], update)

    def set_header_groups(self, groups, update=True):
        for group in groups:
            if not isinstance(group, HeaderGroup):
                group = HeaderGroup.from_json(group)
            if not update or group.id not in self._db.db['headers'].keys():
                self._db.db['headers'][group.id] = group.to_dict()
            if update:
                self._db.db['headers'][group.id].update(group.to_dict())

    def remove_header_group(self, group):
        if not isinstance(group, HeaderGroup):
            group = HeaderGroup.from_json(group)
        if group.id in self._db.db['header'].keys():
            del self._db.db['headers'][group]

    def get_next_group_id(self):
        existing_ids = []
        [existing_ids.extend(e) for e in self._db.db['headers'].values()]
        new_id = random.getrandbits(32)
        while new_id in existing_ids:
            new_id = random.getrandbits(32)
        return new_id

    def get_default_event_header_ids(self, event_key):
        if 'default' in self._db.db['user_event_headers'].keys() \
                and event_key in self._db.db['user_event_headers']['default'].keys():
            return self._db.db['user_event_headers']['default'][event_key]
        return []

    def get_user_event_header_ids(self, user_id, event_key):
        headers = self.get_default_event_header_ids(event_key)
        if user_id in self._db.db['user_event_headers'].keys() \
                and event_key in self._db.db['user_event_headers'][user_id].keys():
            headers.update(self._db.db['user_event_headers'][event_key])
        return headers

    def set_default_header_id_for_page(self, event_key, path, id):
        if 'default' not in self._db.db['user_event_headers'].keys():
            self._db.db['user_event_headers']['default'] = {}
        if event_key not in self._db.db['user_event_headers']['default'].keys():
            self._db.db['user_event_headers']['default'][event_key] = {}
        self._db.db['user_event_headers']['default'][event_key][path] = id
        print(self._db.db['user_event_headers']['default'][event_key])

    def set_user_default_header_id_for_page(self, user_id, event_key, path, id):
        if user_id not in self._db.db['user_event_headers'].keys():
            self._db.db['user_event_headers'][user_id] = {}
        if event_key not in self._db.db['user_event_headers'][user_id].keys():
            self._db.db['user_event_headers'][user_id][event_key] = {}
        self._db.db['user_event_headers'][user_id][event_key][path] = id

    def get_auto_generated_headers(self, event_key, pages=('/a/a', '/a/e', '/a/t')):
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
                if '/a/t' in pages:
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
            if '/a/t' in pages:
                headers['/a/t'] = team_raw_headers
            if '/a/a' in pages:
                headers['/a/a'] = avg_headers

        return headers

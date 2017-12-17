import secrets

from models import HeaderGroup


class HeadersDatabaseInteractor:
    def __init__(self, db):
        self._db = db

        if 'headers' not in self._db.db.keys():
            self._db.db['headers'] = {}
            self._db.commit()

    def get_header_groups(self, event_key):
        if event_key in self._db.db['headers'].keys():
            return [HeaderGroup.from_json(e) for e in self._db.db['headers'][event_key].values()]
        self._db.db['headers'][event_key] = {}
        return []

    def create_header_group(self, event_key, creator_id, path):
        return HeaderGroup('New Group', event_key, creator_id, path, [], self.get_next_group_id(event_key))

    def set_header_group(self, event_key, group, update=True):
        self.set_header_groups(event_key, [group], update)

    def set_header_groups(self, event_key, groups, update=True):
        for group in groups:
            if not isinstance(group, HeaderGroup):
                group = HeaderGroup.from_json(group)
            if not update or group.id not in self._db.db['headers'][event_key].keys():
                self._db.db['headers'][event_key][group.id] = group.to_dict()
            if update:
                self._db.db['headers'][event_key][group.id].update(group.to_dict())

    def remove_header_group(self, event_key, group):
        if not isinstance(group, HeaderGroup):
            group = HeaderGroup.from_json(group)
        if group.id in self._db.db['header'][event_key].keys():
            del self._db.db['headers'][event_key][group]

    def get_next_group_id(self, event_key):
        existing_ids = []
        [existing_ids.extend(e) for e in self._db.db['headers'][event_key].values()]
        new_id = secrets.randbits(32)
        while new_id in existing_ids:
            new_id = secrets.randbits(32)
        return new_id
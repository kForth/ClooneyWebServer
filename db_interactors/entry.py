from models import ScoutingEntry


class EntryDatabaseInteractor:
    def __init__(self, db, app):
        self._db = db
        self._app = app

    def get_entry_by_id(self, id):
        return ScoutingEntry.from_json(self._db.db['entry']['entry'][id]) if id in self._db.db['entry']['entry'].keys() else None

    def remove_entry(self, id):
        if id in self._db.db['entry']['entry'].keys():
            del self._db.db['entry']['entry'][id]
            self._db.commit()

    def set_entry(self, entry):
        self._db['entry']['entry'][entry.id] = entry.to_dict()
        self._db.commit()

    def get_next_entry_id(self):
        return int(self._db.db['users']['max_id'] + 1)

from models import ScoutingEntry


class EntryDatabaseInteractor:
    def __init__(self, db):
        self._db = db

    def get_entries(self):
        return self._db.db['entry']['entry']

    def get_entry_by_id(self, id):
        return ScoutingEntry.from_json(self.get_entries()[id]) if id in self.get_entries().keys() else None

    def remove_entry(self, id):
        if id in self.get_entries().keys():
            del self.get_entries()[id]
            self._db.commit()

    def set_entry(self, entry):
        self.get_entries()[entry.id] = entry.to_dict()
        self._db.commit()

    def get_next_entry_id(self):
        return int(self._db.db['users']['max_id'] + 1)

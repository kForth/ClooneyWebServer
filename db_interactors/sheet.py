import json


class SheetDatabaseInteractor:
    def __init__(self, db, app):
        self._db = db
        self.default_fields = json.load(open(app.root_path + "/db/field_settings.json"))

    def get_sheets(self):
        return self._db.db['sheets']

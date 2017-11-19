import json


class SheetDatabaseInteractor:
    def __init__(self, db, app):
        self._db = db
        self._app = app
        self.default_fields = json.load(open(app.root_path + "/field_settings.json"))

    def get_sheets(self):
        return self._db.db['sheets']

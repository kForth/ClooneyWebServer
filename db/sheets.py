import json

from flask import jsonify, make_response


class SheetDatabaseInteractor:
    def __init__(self, db, app):
        self._db = db
        self._app = app

        self.default_fields = json.load(open(app.root_path + "/field_settings.json"))
        self._app.add_url_rule('/get/sheets', '/get/sheets', self.get_sheets, methods=('GET',))
        self._app.add_url_rule('/get/default_fields', '/get/default_fields', self.get_default_fields, methods=('GET',))

    def get_sheets(self):
        return make_response(jsonify(self._db.get_sheets()), 200)

    def get_default_fields(self):
        return make_response(jsonify(self.default_fields), 200)

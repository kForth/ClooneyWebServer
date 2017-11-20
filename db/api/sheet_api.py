from flask import jsonify, make_response


class SheetDatabaseEndpoints:
    def __init__(self, db, app):
        self._db = db
        self._app = app

        self._app.add_route('/get/sheets', self.get_sheets)
        self._app.add_route('/get/default_fields', self.get_default_fields)

    def get_sheets(self):
        return make_response(jsonify(self._db.get_sheets()), 200)

    def get_default_fields(self):
        return make_response(jsonify(self._db.default_fields), 200)

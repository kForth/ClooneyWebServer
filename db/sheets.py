from flask import make_response, jsonify


class SheetDatabaseInteractor:
    def __init__(self, db, app):
        self._db = db
        self._app = app

        self._app.add_url_rule('/get/sheets', '/get/sheets', self.get_sheets, methods=('GET',))

    def get_sheets(self):
        return make_response(jsonify(self._db.get_sheets()), 200)

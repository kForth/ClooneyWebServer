from flask import jsonify, make_response


class SheetDatabaseEndpoints:
    def __init__(self, db_interactor, add_route):
        self._db_interactor = db_interactor

        add_route('/get/sheets', self.get_sheets)
        add_route('/get/default_fields', self.get_default_fields)

    def get_sheets(self):
        return make_response(jsonify(self._db_interactor.get_sheets()), 200)

    def get_default_fields(self):
        return make_response(jsonify(self._db_interactor.default_fields), 200)

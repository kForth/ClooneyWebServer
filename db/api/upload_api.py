from flask import request, jsonify, make_response


class UploadDatabaseEndpoints:
    def __init__(self, db, app):
        self._db = db
        self._app = app

        self._app.add_route('/add/entry', self.add_entry(), ('POST',))

    def add_entry(self):
        if request.json():
            return make_response(jsonify(), 200)
        return make_response(jsonify(), 400)

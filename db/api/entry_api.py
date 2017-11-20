from flask import request, jsonify, make_response

from db.models import ScoutingEntry


class EntryDatabaseEndpoints:
    def __init__(self, db_interactor, app):
        self._db_interactor = db_interactor
        self._app = app

        self._app.add_route('/add/entry', self.add_entry(), ('POST',))

    def add_entry(self):
        entry = ScoutingEntry.from_json(request.json)
        existing = self._db_interactor.get_entry_by_id(entry.id)
        if entry:
            if existing:
                return make_response(jsonify({'existing': existing.to_json()}), 409)
            else:
                self._db_interactor.set_entry(entry)
                return make_response(jsonify(), 200)
        return make_response(jsonify(), 400)

    def remove_entry(self, id):
        return make_response(jsonify(), 200 if self._db_interactor.remove_entry(id) else 400)

    def update_entry(self):
        entry = ScoutingEntry.from_json(request.json)
        if self._db_interactor.get_entry_by_id(entry.id):
            self._db_interactor.remove_entry(entry.id)
            self._db_interactor.set_entry(entry)
            return make_response(jsonify(), 200)
        return make_response(jsonify(), 404)

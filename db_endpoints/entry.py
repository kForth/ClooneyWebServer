from flask import jsonify, make_response, request

from models import ScoutingEntry


class EntryDatabaseEndpoints:
    def __init__(self, db_interactor, add_route):
        self._db_interactor = db_interactor

        add_route('/add/entry', self.add_entry, ('POST',))
        add_route('/get/raw_entries/<event_key>', self.get_entries)

    def get_entries(self, event_key):
        entries = [e.to_dict() for e in self._db_interactor.get_entries() if e.event == event_key]
        return make_response(jsonify(entries), 200 if entries else 404)

    def add_entry(self):
        entry = request.json
        entry['id'] = self._db_interactor.get_next_entry_id()
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

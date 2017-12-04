from flask import make_response, jsonify


class CalculatorDatabaseEndpoints:
    def __init__(self, db_interactor, add_route):
        self._db_interactor = db_interactor

        add_route('/update/entries/<event_key>', self.update_entries_for_event, methods=('POST',))

    def update_entries_for_event(self, event_key):
        print(event_key)
        status = self._db_interactor.update_entries_for_event(event_key)
        return make_response(jsonify(), 200 if status else 400)

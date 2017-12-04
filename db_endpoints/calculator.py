import traceback

from flask import abort


class CalculatorDatabaseEndpoints:
    def __init__(self, db_interactor, add_route):
        self._db_interactor = db_interactor

        add_route('/update/event_analysis/<event_key>', self.update_entries_for_event, methods=('POST',))

    def update_entries_for_event(self, event_key):
        try:
            self._db_interactor.update_entries_for_event(event_key)
            return "Update Successful", 200
        except Exception as ex:
            traceback.print_exc()
            return abort(400)

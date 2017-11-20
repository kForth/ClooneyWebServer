from flask import jsonify, make_response, request


class EventDatabaseEndpoints:
    def __init__(self, db_interactor, add_route):
        self._db_interactor = db_interactor

        add_route('/get/available_events', self.get_available_events)

        add_route('/get/search_events', self.get_search_events, methods=('GET',))
        add_route('/setup_tba_event', lambda: self.setup_event(use_tba=True), ('POST',))
        add_route('/setup_event', self.setup_event, ('POST',))

    def get_search_events(self):
        return make_response(jsonify(self._db_interactor.get_search_events()), 200)

    def get_available_events(self):
        return make_response(jsonify(self._db_interactor.get_events()), 200)

    def setup_event(self, use_tba=False):
        if request.json:
            data = request.json
            if data['key'] not in self._db_interactor.get_event_keys():
                event = {
                    'key': data['key'],
                    'entries': [],
                    'info':    {
                        'data':    {} if use_tba else {
                            'is_tba':         False,
                            'name': data      ['name'],
                            'short_name': data['short_name']
                        },
                        'teams':   data['teams'] if 'teams' in data.keys() else [],
                        'matches': data['matches'] if 'matches' in data.keys() else []
                    }
                }
                self._db_interactor.set_event(data['key'], event)
                if use_tba:
                    self._db_interactor.update_event_details(data['key'])
                    self._db_interactor.update_event_teams(data['key'])
                    self._db_interactor.update_event_matches(data['key'])
                return make_response(jsonify(), 200)
            else:
                return make_response(jsonify(), 409)
        else:
            return make_response(jsonify(), 400)

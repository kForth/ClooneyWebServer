from flask import jsonify, make_response, request


class EventDatabaseEndpoints:
    def __init__(self, db, app):
        self._db = db
        self._app = app

        self._app.add_route('/get/available_events', self.get_available_events)

        self._app.add_route('/setup_tba_event', lambda: self.setup_event(use_tba=True), ('POST',))
        self._app.add_route('/setup_event', self.setup_event, ('POST',))

    def get_available_events(self):
        return make_response(jsonify(sorted(self._db.get_events(), key=lambda k: k['name'])), 200)

    def setup_event(self, use_tba=False):
        if request.json:
            data = request.json
            if data['key'] not in self._db.db['events'].keys():
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
                self._db.db['events'][data['key']] = event
                self._db.commit()
                if use_tba:
                    self._db.update_event_details(data['key'])
                    self._db.update_event_teams(data['key'])
                    self._db.update_event_matches(data['key'])
                return make_response(jsonify(), 200)
            else:
                return make_response(jsonify(), 409)
        else:
            return make_response(jsonify(), 400)

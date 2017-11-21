from flask import jsonify, make_response, request

from models import Event


class EventDatabaseEndpoints:
    def __init__(self, db_interactor, add_route):
        self._db_interactor = db_interactor

        add_route('/get/available_events', self.get_available_events)
        add_route('/get/event/<key>', self.get_event)
        add_route('/get/search_events', self.get_search_events, methods=('GET',))
        add_route('/setup_tba_event', lambda: self.setup_event(use_tba=True), ('POST',))
        add_route('/setup_event', self.setup_event, ('POST',))

        add_route('/get/calculations', self.get_calculations)
        add_route('/set/calculations', self.set_calculations, methods=('POST',))

    def get_event(self, key):
        event = self._db_interactor.get_event(key)
        if event:
            return make_response(jsonify(event.to_dict()), 200)
        return make_response(jsonify(), 404)

    def get_calculations(self):
        pass

    def set_calculations(self):
        pass

    def get_search_events(self):
        return make_response(jsonify(self._db_interactor.get_search_events()), 200)

    def get_available_events(self):
        return make_response(jsonify(self._db_interactor.get_events_data()), 200)

    def setup_event(self, use_tba=False):
        if request.json:
            data = request.json
            if data['key'] not in self._db_interactor.get_event_keys():
                print(data)
                data['info'] = {
                    'is_tba': use_tba,
                    'data': {
                        'name': data['short_name'] if 'short_name' in data.keys() else data['key'],
                        'short_name': data['name'] if 'name' in data.keys() else data['key']
                    }
                }
                event = Event.from_json(data)
                self._db_interactor.set_event(data['key'], event)
                if use_tba:
                    self._db_interactor.update_event_details(event.key)
                    self._db_interactor.update_event_teams(event.key)
                    self._db_interactor.update_event_matches(event.key)
                return make_response(jsonify(event.to_dict()), 200)
            else:
                return make_response(jsonify(), 409)
        else:
            return make_response(jsonify(), 400)

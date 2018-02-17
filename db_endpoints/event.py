from flask import jsonify, make_response, request

from models import Event


class EventDatabaseEndpoints:
    def __init__(self, db_interactor, add_route):
        self._db_interactor = db_interactor

        add_route('/get/available_events', self.get_available_events)
        add_route('/get/event/<key>', self.get_event)
        add_route('/get/event_matches/<key>', self.get_event_matches)
        add_route('/get/event_settings/<key>', self.get_event_settings)
        add_route('/set/event_settings/<key>', self.set_event_settings, methods=('POST',))
        add_route('/get/search_events', self.get_search_events, methods=('GET',))
        add_route('/setup_tba_event', lambda: self.setup_event(use_tba=True), ('POST',))
        add_route('/update/tba/<event>', self.update_tba_event)
        add_route('/setup_event', self.setup_event, ('POST',))

        add_route('/get/calculations', self.get_calculations)
        add_route('/set/calculations', self.set_calculations, methods=('POST',))

    def get_event(self, key):
        event = self._db_interactor.get_event(key)
        if event:
            return make_response(jsonify(event.to_dict()), 200)
        return make_response(jsonify(), 404)

    def get_event_matches(self, key):
        event = self._db_interactor.get_event(key)
        if event:
            return make_response(jsonify(event.matches), 200)
        return make_response(jsonify(), 404)

    def get_event_settings(self, key):
        settings = self._db_interactor.get_event_settings(key)
        return make_response(jsonify(settings), 200 if settings else 400)

    def set_event_settings(self, key):
        settings = request.json
        if settings:
            self._db_interactor.set_event_settings(key, settings)
            return make_response(jsonify(), 200)
        return make_response(jsonify(), 400)

    def get_calculations(self):
        pass

    def set_calculations(self):
        pass

    def update_tba_event(self, event):
        try:
            self._db_interactor.update_event_details(event)
            self._db_interactor.update_event_matches(event)
            self._db_interactor.update_event_teams(event)
            return make_response(jsonify(), 200)
        except Exception as ex:
            return make_response(jsonify(), 400)

    def get_search_events(self):
        return make_response(jsonify(self._db_interactor.get_search_events()), 200)

    def get_available_events(self):
        return make_response(jsonify(self._db_interactor.get_events_data()), 200)

    def setup_event(self, use_tba=False):
        if request.json:
            data = request.json
            if data['key'] not in self._db_interactor.get_event_keys():
                data['info'] = {
                    'is_tba': use_tba,
                    'data': {
                        'name': data['short_name'] if 'short_name' in data.keys() else data['key'],
                        'short_name': data['name'] if 'name' in data.keys() else data['key']
                    }
                }
                event = Event.from_json(data)
                self._db_interactor.set_event(data['key'], event)
                self._db_interactor.set_event_settings(data['key'])
                if use_tba:
                    self._db_interactor.update_event_details(event.key)
                    self._db_interactor.update_event_teams(event.key)
                    self._db_interactor.update_event_matches(event.key)
                return make_response(jsonify(event.to_dict()), 200)
            else:
                return make_response(jsonify(), 409)
        else:
            return make_response(jsonify(), 400)
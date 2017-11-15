from flask import make_response, jsonify

from tba_py import TBA


class TbaInteractor:
    def __init__(self, db, app):
        self._db = db
        self._app = app
        self._tba = TBA(app.config['TBA_AUTH_KEY'])

        self._app.add_url_rule('/get/search_events', '/get/search_events', view_func=self.get_search_events, methods=('GET',))

    def get_search_events(self):
        events = []
        events += self._tba.get_events_simple(2018)
        events += self._tba.get_events_simple(2017)

        return make_response(jsonify(sorted(events, key=lambda k: k['name'])), 200)

    def update_event_details(self, key):
        event = self._db.get_event(key)
        event['info']['data'] = self._tba.get_event_info(key)
        event['info']['data']['is_tba'] = True
        self._db.set_event(key, event)
        self._db.commit()

    def update_event_teams(self, key):
        event = self._db.get_event(key)
        event['info']['teams'] = self._tba.get_event_teams(key)
        self._db.set_event(key, event)
        self._db.commit()

    def update_event_matches(self, key):
        event = self._db.get_event(key)
        event['info']['matches'] = self._tba.get_event_matches(key)
        self._db.set_event(key, event)
        self._db.commit()

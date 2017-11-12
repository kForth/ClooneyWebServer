from flask import make_response, jsonify

from tba import TBA


class TbaInteractor:
    def __init__(self, db, tba_auth_key, add_url_rule):
        self._db = db
        self._tba = TBA(tba_auth_key)
        self._add_url_rule = add_url_rule

        self._add_url_rule('/get/search_events', '/get/search_events', view_func=self.get_search_events, methods=('GET',))

    def get_search_events(self):
        events = []
        events += self._tba.get_events_simple(2018)
        events += self._tba.get_events_simple(2017)

        return make_response(jsonify(sorted(events, key=lambda k: k['name'])), 200)

    def update_event_details(self, key):
        event = self._db.get_event(key)
        event['info']['data'] = self._tba.get_event_info(key)
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

from flask import request, make_response, jsonify

import json
from os import path

from db.tba import TbaInteractor


class DatabaseInteractor:
    DEFAULT_DB = {'events': {}, 'users': {}}

    def __init__(self, folder_path, add_url_rule, tba_auth_key, filename="db.json"):
        self.filepath = folder_path + ("" if folder_path[-1] == "/" else "/") + filename
        self._add_url_rule = add_url_rule
        self._db = self._load_db()
        self._tba = TbaInteractor(self, tba_auth_key, add_url_rule)

        self._add_url_rule('/get/available_events', '/get/available_events', view_func=self.get_available_events, methods=('GET',))
        self._add_url_rule('/setup_tba_event', '/setup_tba_event', view_func=lambda: self.setup_event(use_tba=True), methods=('POST',))
        self._add_url_rule('/setup_event', '/setup_event', view_func=self.setup_event, methods=('POST',))

    def _load_db(self):
        if path.isfile(self.filepath):
            return json.load(open(self.filepath))
        else:
            json.dump(self.DEFAULT_DB, open(self.filepath, "w+"))
            return self._load_db()

    def commit(self):
        json.dump(self._db, open(self.filepath, "w+"))

    def get_available_events(self):
        return make_response(jsonify(sorted(self.get_events(), key=lambda k: k['name'])), 200)

    def get_events(self):
        return list(map(lambda x: x['info']['data'], self._db['events'].values()))

    def get_event(self, key):
        return self._db['events'][key]

    def set_event(self, key, data):
        self._db['events'][key] = data

    def setup_event(self, use_tba=False):
        if request.json:
            data = request.json
            print(data)
            if data['key'] not in self._db['events'].keys():
                event = {
                    'key': data['key'],
                    'entries': [],
                    'info': {
                        'data': {} if use_tba else {
                            'is_tba': False,
                            'name': data['name'],
                            'short_name': data['short_name']
                        },
                        'teams': data['teams'] if 'teams' in data.keys() else [],
                        'matches': data['matches'] if 'matches' in data.keys() else []
                    }
                }
                self._db['events'][data['key']] = event
                self.commit()
                if use_tba:
                    self._tba.update_event_details(data['key'])
                    self._tba.update_event_teams(data['key'])
                    self._tba.update_event_matches(data['key'])
                return make_response(jsonify(), 200)
            else:
                return make_response(jsonify(), 409)
        else:
            return make_response(jsonify(), 400)

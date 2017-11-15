from flask import request, make_response, jsonify

import json
from os import path

from db.tba import TbaInteractor
from db.user import UserDatabaseInteractor


class DatabaseInteractor:
    DEFAULT_DB = {'events': {}, 'users': {'users': [], 'max_id': -1}}

    def __init__(self, app, filename="db.json"):
        self.filepath = app.root_path + "/" + filename
        self._app = app
        self._db = self._load_db()
        self._users = UserDatabaseInteractor(self, app)
        self._tba = TbaInteractor(self, app)

        self._app.add_url_rule('/get/available_events', '/get/available_events', view_func=self.get_available_events, methods=('GET',))

        self._app.add_url_rule('/setup_tba_event', '/setup_tba_event', view_func=lambda: self.setup_event(use_tba=True), methods=('POST',))
        self._app.add_url_rule('/setup_event', '/setup_event', view_func=self.setup_event, methods=('POST',))

    def _load_db(self):
        if path.isfile(self.filepath):
            return json.load(open(self.filepath))
        else:
            json.dump(self.DEFAULT_DB, open(self.filepath, "w+"))
            return self._load_db()

    def commit(self):
        json.dump(self._db, open(self.filepath, "w+"))

    def get_users(self):
        return self._db['users']['users']

    def get_user_by_id(self, user_id):
        user = [e for e in self._db['users'] if e['id'] == user_id]
        return dict(user[0]) if user else None

    def get_user_by_name(self, username):
        user = [e for e in self._db['users']['users'] if e['username'].lower() == username.lower()]
        print(user)
        return dict(user[0]) if user else None

    def add_user(self, user):
        user['id'] = self.get_next_id()
        self._db['users']['max_id'] += 1
        self._db['users']['users'].append(user)

    def remove_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            self._db['users']['users'].remove(user)

    def update_user(self, user_id, user):
        old = self.get_user_by_id(user_id)
        old.update(user)
        self._db['users']['users'].remove(user)
        self._db['users']['users'].append(old)

    def get_next_id(self):
        return int(self._db['users']['max_id'] + 1)

    def get_available_events(self):
        return make_response(jsonify(sorted(self.get_events(), key=lambda k: k['name'])), 200)

    def get_events(self):
        return list(map(lambda x: x['info']['data'], self._db['events'].values()))

    def get_event(self, key):
        return dict(self._db['events'][key])

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

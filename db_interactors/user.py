import hmac
import json
from hashlib import sha1

from models import User, UserSettings


class UserDatabaseInteractor:
    ROLES = ['Guest', 'User', 'Editor', 'Admin']

    def __init__(self, db, app):
        self._db = db
        self._app = app

    def encrypt_password(self, pwd):
        hash = hmac.new(str(self._app.config['PASSWORD_KEY']).encode('UTF-8'), msg=str(pwd).encode('UTF-8'),
                        digestmod=sha1)
        return hash.hexdigest()

    def verify_password(self, pwd, hash):
        pwd = self.encrypt_password(pwd)
        return hmac.compare_digest(str(pwd).encode('UTF-8'), str(hash).encode('UTF-8'))

    def get_users(self):
        return self._db.db['users']['users']

    def get_user_by_id(self, user_id):
        user = [e for e in self.get_users() if e['id'] == user_id]
        return User.from_json(user[0]) if user else None

    def get_user_by_username(self, username):
        user = [e for e in self.get_users() if e['username'].lower() == username.lower()]
        return User.from_json(user[0]) if user else None

    def get_user_settings_by_user_username(self, username):
        if username in self._db.db['user_settings'].keys():
            return UserSettings.from_json(self._db.db['user_settings'][username])
        return None

    def update_event_headers_by_user_id(self, user_id, event_key, data):
        if user_id not in self._db.db['user_event_headers'].keys():
            self._db.db['user_event_headers'][user_id] = {}
        if event_key not in self._db.db['user_event_headers'][user_id].keys():
            self._db.db['user_event_headers'][user_id][event_key] = {}
        self._db.db['user_event_headers'][user_id][event_key].update(data)

    def get_default_event_headers(self, event_key):
        # TODO: Uncomment these and just update them if the sheet or calculations change
        # if 'default' in self._db.db['user_event_headers'].keys() and event_key in self._db.db['user_event_headers']['default'].keys():
        #     return self._db.db['user_event_headers']['default'][event_key]
        return self.update_default_event_headers(event_key)

    def update_default_event_headers(self, event_key):
        headers = {
            '/a/a': [],
            '/a/e': []
        }
        event_sheet = json.loads(self._db.db['event_settings'][event_key]['selected_sheet'])['data']
        if event_sheet:
            raw_headers = [
                {
                    "data_key":   "match",
                    "class":      "",
                    "title":      "M#",
                    "data_class": "",
                    "tooltip":    ""
                },
                {
                    "data_key":   "pos",
                    "class":      "",
                    "title":      "P#",
                    "data_class": "",
                    "tooltip":    ""
                },
                {
                    "data_key":   "team",
                    "class":      "",
                    "title":      "Team",
                    "data_class": "",
                    "tooltip":    ""
                },
            ]
            avg_headers = [dict(e) for e in raw_headers]
            del avg_headers[1]
            avg_headers[0]['data_key'] += '.count'
            avg_headers[1]['data_key'] += '.mode'
            for line in event_sheet:
                if line['type'] in ['Image', 'Divider']:
                    continue
                header = {
                    "data_key":   line['key'],
                    "class":      "",
                    "title":      line['label'],
                    "data_class": "",
                    "tooltip":    ""
                }
                raw_headers.append(dict(header))
                if line['type'] == 'Numbers':
                    header["data_key"] += ".avg"
                elif line['type'] == 'Boolean':
                    header["data_key"] += ".mode"
                elif line['type'] == 'HorizontalOptions':
                    header["data_key"] += ".mode"
                avg_headers.append(header)

            headers['/a/e'] = raw_headers
            headers['/a/a'] = avg_headers

            if 'default' not in self._db.db['user_event_headers'].keys():
                self._db.db['user_event_headers']['default'] = {}
            self._db.db['user_event_headers']['default'][event_key] = headers

        return headers

    def get_event_headers_by_user_id(self, user_id, event_key):
        if user_id in self._db.db['user_event_headers'].keys():
            if event_key in self._db.db['user_event_headers'][user_id].keys():
                headers = self._db.db['user_event_headers'][event_key]
                return headers if headers else self.get_default_event_headers(event_key)
        return {}

    def set_user_settings(self, username, settings):
        self._db.db['user_settings'][username] = settings.to_dict()

    def add_user(self, user):
        user = user.to_dict()
        self.get_users().append(user)

    def remove_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            self.get_users().remove(user)

    def update_user(self, user_id, user):
        old = self.get_user_by_id(user_id).to_dict()
        old.update(user.to_dict)
        self.get_users().remove(user)
        self.get_users().append(old)

    def get_next_user_id(self):
        self._db.db['users']['max_id'] += 1
        return self._db.db['users']['max_id']

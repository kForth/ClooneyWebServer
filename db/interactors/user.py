from hashlib import sha1
import hmac

from db.api.user_api import UserDatabaseEndpoints


class UserDatabaseInteractor:
    ROLES = ['Guest', 'User', 'Editor', 'Admin']

    def __init__(self, db, app):
        self._db = db
        self._app = app
        self.commit = self._db.commit
        self._endpoints = UserDatabaseEndpoints(self, app)

    def encrypt_password(self, pwd):
        hash = hmac.new(str(self._app.config['PASSWORD_KEY']).encode('UTF-8'), msg=str(pwd).encode('UTF-8'), digestmod=sha1)
        return hash.hexdigest()

    def verify_password(self, pwd, hash):
        pwd = self.encrypt_password(pwd)
        return hmac.compare_digest(str(pwd).encode('UTF-8'), str(hash).encode('UTF-8'))

    def get_user_by_id(self, user_id):
        user = [e for e in self._db.db['users'] if e['id'] == user_id]
        return dict(user[0]) if user else None

    def get_user_by_name(self, username):
        user = [e for e in self._db.db['users']['users'] if e['username'].lower() == username.lower()]
        return dict(user[0]) if user else None

    def add_user(self, user):
        user['id'] = self.get_next_user_id()
        self._db.db['users']['max_id'] += 1
        self._db.db['users']['users'].append(user)

    def remove_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            self._db.db['users']['users'].remove(user)

    def update_user(self, user_id, user):
        old = self.get_user_by_id(user_id)
        old.update(user)
        self._db.db['users']['users'].remove(user)
        self._db.db['users']['users'].append(old)

    def get_next_user_id(self):
        return int(self._db.db['users']['max_id'] + 1)
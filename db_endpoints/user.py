import json
import time
from flask import make_response, jsonify, request

from models import User, UserSettings


class UserDatabaseEndpoints:
    ROLES = ['Guest', 'User', 'Editor', 'Admin']
    DEFAULT_USER_SETTINGS = json.load(open('db/default_user_settings.json'))

    def __init__(self, db_interactor, add_route, active_users):
        self._db_interactor = db_interactor
        self._active_users = active_users

        add_route('/login', self.login_user, ('POST',))
        add_route('/logout', self.logout_user, ('POST',))
        add_route('/users/create/', self.register_user, ('POST',))
        add_route('/users/update/<id>', self.get_user_by_username, ('POST',))
        add_route('/get/user_settings/<username>', self.get_user_settings)
        add_route('/get/user_settings/', self.get_user_settings)

    def get_user_settings(self, username=None):
        if username:
            user_settings = self._db_interactor.get_user_settings_by_user_username(username.lower())
            if user_settings:
                return make_response(jsonify(user_settings.to_dict()), 200)
        elif username:
            self._db_interactor.set_user_settings(username.lower(), UserSettings.from_json(self.DEFAULT_USER_SETTINGS))
        return make_response(jsonify(self.DEFAULT_USER_SETTINGS), 200)

    def get_user_by_id(self, id):
        user = self._db_interactor.get_user_by_id(id)
        if user:
            user = user.to_json()
            user['password'] = ''
            return make_response(jsonify(user), 200)
        return make_response(jsonify(), 404)

    def get_user_by_username(self, username):
        user = self._db_interactor.get_user_by_username(username.low)
        if user:
            user = user.to_json()
            user['password'] = ''
            return make_response(jsonify(user), 200)
        return make_response(jsonify(), 404)

    def register_user(self):
        user_data = request.json
        user_data['id'] = self._db_interactor.get_next_user_id()
        user = User.from_json(request.json)
        if user:
            existing = self._db_interactor.get_user_by_username(user.username)
            if not existing:
                user.role = self.ROLES[0]
                user.password = self._db_interactor.encrypt_password(user.password)
                self._db_interactor.add_user(user)
                return make_response(jsonify(), 200)
        return make_response(jsonify(), 400)

    def update_user(self, id):
        user = User.from_json(request.json())
        existing = self._db_interactor.get_user_by_id(id)
        if user and existing:
            if self._db_interactor.verify_password(user.password_hash, existing.password_hash):
                self._db_interactor.update_user(id, user)
                return make_response(jsonify(), 200)
        return make_response(jsonify(), 400)

    def login_user(self):
        credentials = request.json
        if all([e in credentials.keys() for e in ['username', 'password']]):
            username = credentials['username']
            password = credentials['password']
            user = self._db_interactor.get_user_by_username(username)
            if user and self._db_interactor.verify_password(password, user.password):
                response = {
                    'id': user.id,
                    'key': self._db_interactor.encrypt_password(username + str(time.time())),
                    'user': {
                        'id': user.id,
                        'username': username,
                        'role': self.ROLES.index(user.role),
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    }
                }
                self._active_users[username] = {
                    'key': response['key'],
                    'expiration': time.time() + 604800
                }
                return make_response(jsonify(response), 200)
            else:
                return make_response(jsonify(), 400)
        else:
            return make_response(jsonify(), 409)

    def logout_user(self):
        return make_response(jsonify(), 200)

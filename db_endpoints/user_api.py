from flask import make_response, jsonify, request

from models import User


class UserDatabaseEndpoints:
    ROLES = ['Guest', 'User', 'Editor', 'Admin']

    def __init__(self, db_interactor, add_route):
        self._db_interactor = db_interactor

        add_route('/login', self.login_user, ('POST',))
        add_route('/logout', self.logout_user, ('POST',))
        add_route('/users/create/', self.register_user, ('POST',))
        add_route('/users/update/<id>', self.get_user_by_username, ('POST',))

    def get_user_by_id(self, id):
        user = self._db_interactor.get_user_by_id(id)
        if user:
            user = user.to_json()
            user['password'] = ''
            return make_response(jsonify(user), 200)
        return make_response(jsonify(), 404)

    def get_user_by_username(self, username):
        user = self._db_interactor.get_user_by_username(username)
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
                    'key': 1234567890,
                    'user': {
                        'id': user.id,
                        'username': username,
                        'role': self.ROLES.index(user.role),
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    }
                }
                return make_response(jsonify(response), 200)
            else:
                return make_response(jsonify(), 400)
        else:
            return make_response(jsonify(), 409)

    def logout_user(self):
        return make_response(jsonify(), 200)

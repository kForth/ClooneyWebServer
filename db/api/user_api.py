from flask import make_response, jsonify, request


class UserDatabaseEndpoints:
    ROLES = ['Guest', 'User', 'Editor', 'Admin']

    def __init__(self, db, app):
        self._db = db
        self._app = app

        self._app.add_url_rule('/login', '/login', view_func=self.login_user, methods=('POST',))
        self._app.add_url_rule('/logout', '/logout', view_func=self.logout_user, methods=('POST',))
        self._app.add_url_rule('/users/create/', '/users/create/', self.register_user, methods=('POST',))
        self._app.add_url_rule('/users/update/<id>', '/users/update/<id>', self.get_user_by_name, methods=('POST',))

    def get_user_by_id(self, id):
        user = self._db.get_user_by_id(id)
        if user:
            user['password'] = ''
            return make_response(jsonify(user), 200)
        return make_response(jsonify(), 404)

    def get_user_by_name(self, name):
        user = self._db.get_user_by_name(name)
        if user:
            user['password'] = ''
            return make_response(jsonify(user), 200)
        return make_response(jsonify(), 404)

    def register_user(self):
        user = request.json
        if 'username' in user.keys():
            existing = self._db.get_user_by_name(user['username'].lower())
            if not existing:
                if 'password' in user.keys():
                    user['role'] = self.ROLES[0]
                    user['password'] = self._db.encrypt_password(user['password'])
                    self._db.add_user(user)
                    self._db.commit()
                    return make_response(jsonify(), 200)
        return make_response(jsonify(), 400)

    def update_user(self, id):
        user = request.json()
        existing = self._db.get_user_by_id(id)
        if existing:
            if self._db.verify_password(user['password'], existing['password']):
                self._db.update_user(id, user)
                self._db.commit()
                return make_response(jsonify(), 200)
        return make_response(jsonify(), 400)

    def login_user(self):
        credentials = request.json
        if all([e in credentials.keys() for e in ['username', 'password']]):
            username = credentials['username']
            password = credentials['password']
            user = self._db.get_user_by_name(username)
            if user and self._db.verify_password(password, user['password']):
                response = {
                    'id': user['id'],
                    'key': 1234567890,
                    'user': {
                        'id': user['id'],
                        'username': username,
                        'role': self.ROLES.index(user['role']),
                        'first_name': user['first_name'],
                        'last_name': user['last_name']
                    }
                }
                return make_response(jsonify(response), 200)
            else:
                return make_response(jsonify(), 400)
        else:
            return make_response(jsonify(), 409)

    def logout_user(self):
        return make_response(jsonify(), 200)
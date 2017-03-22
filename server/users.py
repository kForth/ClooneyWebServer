from flask import jsonify, make_response, request, redirect

from flask_security import SQLAlchemyUserDatastore, Security, logout_user
from flask_security.utils import encrypt_password, verify_password


class UsersServer(object):
    def __init__(self, add: classmethod, user_datastore: SQLAlchemyUserDatastore, security: Security, url_prefix=""):
        self._add = lambda *args, **kwarg: add(*args, **kwarg, url_prefix=url_prefix)
        self.user_datastore = user_datastore
        self.security = security
        self._register_views()

    def _register_views(self):
        self._add('/logout', self.log_out)
        self._add('/login', self.login, methods=['POST'])

    def log_out(self):
        logout_user()
        return redirect(request.args.get('next') or '/')

    def login(self):
        # info = request.json
        print("asdf")
        return make_response(jsonify())

    def authenticate(self, username, password):
        user = self.user_datastore.find_user(email=username)
        if user and username == user.email and verify_password(password, user.password):
            return user
        return None

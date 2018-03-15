from flask import jsonify, make_response, request, redirect, session


class UsersServer(object):
    def __init__(self, add: classmethod, url_prefix=""):
        self._add = lambda *args, **kwarg: add(*args, url_prefix=url_prefix, **kwarg)
        self._register_views()

    def _register_views(self):
        self._add('/logout', self.log_out)
        self._add('/login', self.login, methods=['POST'])
        self._add('/check_auth', self.check_auth)

    def _logout(self):
        session["logged_in"] = False
        session["user_info"] = []

    def _login(self, info):
        session["logged_in"] = True
        session["user_info"] = info

    def check_auth(self):
        if 'user_info' in session.keys() and isinstance(session['user_info'], dict):
            return make_response(jsonify({'user-level': session["user_info"]["user_level"]}), 200)
        else:
            return make_response(jsonify(), 401)

    def log_out(self):
        self._logout()
        return redirect(request.args.get('next') or '/')

    def login(self):
        info = request.json
        user = self.authenticate(info['username'], info['password'])
        return make_response(jsonify(user))

    def authenticate(self, username, password):
        from server.models import User
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            self._login(user.to_dict())
            return user.to_dict()
        self._logout()
        return None

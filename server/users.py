from flask import jsonify, make_response, request, redirect, session
from passlib.hash import pbkdf2_sha256
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


class UsersServer:
    def __init__(self, add: classmethod, sql_db: SQLAlchemy, url_prefix=""):
        self._add = lambda *args, **kwarg: add(*args, url_prefix=url_prefix, **kwarg)
        self._register_views()

    def _register_views(self):
        self._add('/logout', self.log_out)
        self._add('/login', self.login, methods=['POST'])
        self._add('/cached_login', self.cached_login, methods=['POST'])
        self._add('/update/username', self.update_username, methods=['POST'])
        self._add('/update/password', self.update_password, methods=['POST'])
        self._add('/update/name', self.update_name, methods=['POST'])
        self._add('/update/role', self.update_role, methods=['POST'])
        self._add('/check_auth', self.check_auth)

    def _get_user_by_username(self, username):
        return User.query.filter(func.lower(User.username) == func.lower(username)).first()

    def _logout(self):
        session["logged_in"] = False
        session["user"] = None

    def _login(self, user):
        session["logged_in"] = True
        session["user"] = user

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
        if user:
            return make_response(jsonify(user), 200)
        else:
            return make_response("", 401)

    def cached_login(self):
        info = request.json
        user = self.authenticate(info['username'], info['password'])
        if user:
            return make_response(jsonify(user), 200)
        else:
            return make_response("", 401)

    def update_name(self):
        info = request.json
        username = info['username']
        password = info['password']
        user_to_update = info['user_to_update']
        new_name = info['new_name']
        user = session['user']

        if username == user.username:
            if user_to_update.lower() == username.lower():
                user.name = new_username
                self.sql_db.session.commit()
                return make_response("", 200)
            else:
                if pbkdf2_sha256.verify(password, user.password):
                    if user.role_level >= 5:
                        target_user = self._get_user_by_username(user_to_update)
                        if target_user:
                            target_user.name = new_name
                            self.sql_db.session.commit()
                            return "Successfully changed {user_to_update}'s name to {new_username}", 200
                        else:
                            return "Can't find user by the name '{user_to_update}'", 404
                    else:
                        return "You can't change {user_to_update}'s name", 401
                else:
                    return "Wrong Password", 401
        else:
            return "Wrong Username", 401

    def update_username(self):
        info = request.json
        username = info['username']
        password = info['password']
        user_to_update = info['user_to_update']
        new_username = info['new_username']
        user = session['user']
        existing_user = self._get_user_by_username(new_username)
        if existing_user:
            return "User '{new_username}' already exists", 409

        if username == user.username and pbkdf2_sha256.verify(password, user.password):
            if user_to_update.lower() == username.lower():
                user.username = new_username
                self.sql_db.session.commit()
                return make_response("", 200)
            else:
                if user.role_level >= 5:
                    target_user = self._get_user_by_username(user_to_update)
                    if target_user:
                        target_user.username = new_username
                        self.sql_db.session.commit()
                        return "Successfully changed {user_to_update}'s username to {new_username}", 200
                    else:
                        return "Can't find user by the name '{user_to_update}'", 404
                else:
                    return "You can't change {user_to_update}'s username", 401

        else:
            return "Wrong Username or Password", 401

    def update_role(self):
        info = request.json
        username = info['username']
        password = info['password']
        user_to_update = info['user_to_update']
        new_role = info['new_role']
        user = session['user']
        if new_role > user.role:
            return "You can't promote someone higher than yourself ({new_role} > {user.role})", 401

        if username == user.username and pbkdf2_sha256.verify(password, user.password):
            if user_to_update.lower() == username.lower():
                return make_response("You can't change your own role", 401)
            else:
                if user.role_level >= 3:
                    target_user = self._get_user_by_username(user_to_update)
                    if target_user:
                        target_user.role = new_role
                        self.sql_db.session.commit()
                        return "Successfully changed {user_to_update}'s username to {new_username}", 200
                    else:
                        return "Can't find user by the name '{user_to_update}'", 404
                else:
                    return "You can't change {user_to_update}'s username", 401

        else:
            return "Wrong Username or Password", 401

    def update_password(self):
        info = request.json
        username = info['username']
        password = info['password']
        user_to_update = info['user_to_update']
        new_password = info['new_username']
        user = session['user']

        if username == user.username and pbkdf2_sha256.verify(password, user.password):
            if user_to_update.lower() == username.lower():
                user.password = pbkdf2_sha256.hash(password)
                self.sql_db.session.commit()
                return make_response("", 200)
            else:
                if user.role_level >= 5:
                    target_user = self._get_user_by_username(user_to_update)
                    if target_user:
                        target_user.password = pbkdf2_sha256.hash(password)
                        self.sql_db.session.commit()
                        return "Successfully changed {user_to_update}'s password", 200
                    else:
                        return "Can't find user by the name '{user_to_update}'", 404
                else:
                    return "You can't change {user_to_update}'s password", 401

        else:
            return "Wrong Username or Password", 401

    def register(self):
        info = request.json
        existing_user = self._get_user_by_username(username)
        if not existing_user:
            password = pbkdf2_sha256.encrypt(info['password'])
            user = User(username=info['username'], password=password, name=info['name'], role=1)
        return False

    def authenticate(self, username, password):
        from server.models import User
        user = self._get_user_by_username(username)
        if user and pbkdf2_sha256.verify(password, user.password):
            self._login(user)
            expiration_time = int(time.time()) + 604800  # 7 Days
            user_hash = pbkdf2_sha256.hash(username)
            user.api_key = "{expiration_time}|{user_hash}|"
            user = user.to_dict()
            return user
        self._logout()
        return None

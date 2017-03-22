from flask_security import RoleMixin, UserMixin

import json

from server import sql_db as db


class ScoutingEntry(db.Model):
    __tablename__ = "scouting_entries"

    id = db.Column(db.INTEGER, primary_key=True)
    event = db.Column(db.VARCHAR(32), nullable=False)
    team = db.Column(db.INTEGER, nullable=False)
    match = db.Column(db.INTEGER, nullable=False)
    pos = db.Column(db.INTEGER, nullable=False)
    data = db.Column(db.TEXT, nullable=False)
    filename = db.Column(db.VARCHAR(128), nullable=True)

    def __init__(self, event: str, team: int, match: int, pos: int, data: dict, filename=""):
        self.event = event
        self.team = team
        self.match = match
        self.pos = pos
        self.data = data
        if type(self.data) is dict:
            self.data = json.dumps(self.data)
        self.filename = filename

    def get_data(self):
        return json.loads(self.data)

    def __repr__(self):
        return '<Entry {0}: {1} {2})>'.format(self.team, self.match, self.pos)

    def to_dict(self):
        return {
            "id": self.id,
            "team": self.team,
            "event": self.event,
            "match": self.match,
            "pos": self.pos,
            "data": json.loads(self.data),
            "filename": self.filename
        }


class AnalysisEntry(db.Model):
    __tablename__ = "analysis_entry"

    id = db.Column(db.VARCHAR(128), primary_key=True)
    event = db.Column(db.VARCHAR(32), nullable=False)
    team = db.Column(db.INTEGER, nullable=False)
    data = db.Column(db.TEXT, nullable=False)
    key = db.Column(db.VARCHAR(128), nullable=False)

    def __init__(self, id: str, event: str, team: int, data: dict, key: str):
        self.event = event
        self.team = team
        self.data = data
        if type(self.data) is dict:
            self.data = json.dumps(self.data)
        self.key = key
        self.id = id

    def get_data(self):
        return json.loads(self.data)

    def __repr__(self):
        return '<Entry {0}: {1} {2})>'.format(self.team, self.event, self.key)

    def to_dict(self):
        return {
            "id": self.id,
            "team": self.team,
            "event": self.event,
            "data": json.loads(self.data),
            "key": self.key
        }


class OprEntry(db.Model):
    __tablename__ = "oprs"

    team = db.Column(db.INTEGER(), nullable=False)
    event = db.Column(db.VARCHAR(10), nullable=False)
    score_key = db.Column(db.VARCHAR(128), nullable=False)
    value = db.Column(db.REAL(), nullable=False)
    id = db.Column(db.VARCHAR(128), primary_key=True)
    percentile = db.Column(db.REAL(), nullable=False)

    def __init__(self, id, team, event, score_key, value, percentile):
        self.id = id
        self.team = team
        self.event = event
        self.score_key = score_key
        self.value = value
        self.percentile = percentile

    def to_csv(self):
        return ["team", "event", "key", "value", "percentile"], ','.join(
                [self.team, self.event, self.key, self.value, self.percentile])

    def __repr__(self):
        return '<OPR {0}: {1} {2} @ {3} ({4})>'.format(self.team, self.score_key, self.value, self.event,
                                                       self.percentile)

    def to_dict(self):
        return {
            "id": self.id,
            "team": self.team,
            "event": self.event,
            "score_key": self.score_key,
            "value": self.value,
            "percentile": self.percentile
        }


roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

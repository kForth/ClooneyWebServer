import json

from server import sql_db as db


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.VARCHAR(32), primary_key=True)
    tba_info = db.Column(db.TEXT, nullable=True)
    team_list = db.Column(db.TEXT, nullable=True)
    matches = db.Column(db.TEXT, nullable=True)

    def __init__(self, id: str, tba_info: dict, team_list: list, matches: list):
        self.id = id
        self.tba_info = tba_info
        self.team_list = team_list
        self.matches = matches
        if type(self.tba_info) is dict:
            self.tba_info = json.dumps(self.tba_info)
        if type(self.team_list) is list:
            self.team_list = json.dumps(self.team_list)
        if type(self.matches) is list:
            self.matches = json.dumps(self.matches)

    def set_tba_info(self, info: dict):
        self.tba_info = json.dumps(info)

    def set_team_list(self, teams: list):
        self.team_list = json.dumps(teams)

    def set_matches(self, matches: list):
        self.matches = json.dumps(matches)

    def get_team_list(self):
        return json.loads(self.team_list)

    def get_tba_info(self):
        return json.loads(self.tba_info)

    def get_matches(self):
        return json.loads(self.matches)

    def __repr__(self):
        return '<Event {})>'.format(self.id)

    def to_dict(self):
        return {
            "id": self.id,
            "tba_info": json.loads(self.tba_info),
            "team_list": json.loads(self.team_list),
            "matches": json.loads(self.matches)
        }


class LastModifiedEntry(db.Model):
    __tablename__ = "last_modified"

    id = db.Column(db.INTEGER, primary_key=True)
    event = db.Column(db.TEXT, nullable=False)
    key = db.Column(db.TEXT, nullable=False)
    last_modified = db.Column(db.TEXT, nullable=True)


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
        self.update(event, team, match, pos, data, filename)

    def update(self, event: str, team: int, match: int, pos: int, data: dict, filename=""):
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

    def set_data(self, data):
        self.data = data
        if type(self.data) is dict:
            self.data = json.dumps(self.data)

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


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(255), unique=True, nullable=False)
    username = db.Column(db.VARCHAR(255), nullable=False)
    password = db.Column(db.VARCHAR(255), nullable=False)
    role = db.Column(db.INTEGER(), default=1, nullable=False)
    api_key = db.Column(db.VARCHAR(255), nullable=False)

    def __init__(self, name, username, password, role=1, api_key=""):
        self.name = name
        self.username = username
        self.password = password
        self.role = role
        self.api_key = api_key

    def update_api_key(self, new_key):
        self.api_key = new_key
        db.session.commit()

    def to_dict(self):
        return {
            'username': self.username,
            'name': self.name,
            'role': self.role,
            'api_key': self.api_key
        }
        
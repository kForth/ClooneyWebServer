from sqlalchemy.dialects.postgresql import ARRAY, JSON

from server.db import sql_db as db


class Event(db.Model):
    key = db.Column(db.String(16), primary_key=True)
    info = db.Column(JSON)
    year = db.Column(db.Integer)

    def __repr__(self):
        return '<Event {}>'.format(self.key)


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_number = db.Column(db.Integer)
    match_level = db.Column(db.String(16))
    event_key = db.Column(db.String(16), db.ForeignKey('event.key'))
    info = db.Column(JSON)
    teams = db.Column(ARRAY(db.INTEGER, db.ForeignKey('team.number')))

    def get_tba_key(self):
        middle = "m" if self.match_level != "qm" else ""
        return "{0}_{1}{2}{3}".format(self.event_key, self.match_level, middle, self.match_number)

    def __repr__(self):
        return "<Match {}>".format(self.get_tba_key())


class Team(db.Model):
    number = db.Column(db.Integer, primary_key=True)
    info = db.Column(JSON)

    def __repr__(self):
        return '<Team {}>'.format(self.team_num)


class ScoutingEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(16), db.ForeignKey('event.key'))
    team_number = db.Column(db.Integer, db.ForeignKey('team.number'))
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    value = db.Column(JSON)

    def __repr__(self):
        return '<ScoutingEntry {0}:{1} [{2}]>'.format(self.event, self.team_number, self.key)



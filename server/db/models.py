from server.db import sql_db as db


event_teams = db.Table('event_teams',
    db.Column('team_number', db.Integer, db.ForeignKey('team.number')),
    db.Column('event_key', db.String(16), db.ForeignKey('event.key'))
)

match_teams = db.Table('match_teams',
    db.Column('team_number', db.Integer, db.ForeignKey('team.number')),
    db.Column('match_id', db.Integer, db.ForeignKey('match.id'))
)


class Event(db.Model):
    key = db.Column(db.String(16), primary_key=True)
    info = db.Column(db.JSON)
    year = db.Column(db.Integer)

    matches = db.relationship('Match', backref='event', lazy='dynamic')
    scouting_entries = db.relationship('ScoutingEntry', backref='event', lazy='dynamic')
    teams = db.relationship('Team', secondary=event_teams, backref=db.backref('event', lazy='dynamic'))

    def __repr__(self):
        return '<Event {}>'.format(self.id)


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    level = db.Column(db.String(16))
    event_key = db.Column(db.String(16), db.ForeignKey('event.key'))
    info = db.Column(db.JSON)

    scouting_entries = db.relationship('ScoutingEntry', backref='match', lazy='dynamic')
    teams = db.relationship('Team', secondary=match_teams, backref=db.backref('match', lazy='dynamic'))

    def __repr__(self):
        return "<Match {0}{1} @ {2}>".format(self.number, self.level, self.event_key)


class Team(db.Model):
    number = db.Column(db.Integer, primary_key=True)
    info = db.Column(db.JSON)

    scouting_entries = db.relationship('ScoutingEntry', backref='team', lazy='dynamic')
    events = db.relationship('Event', secondary=event_teams, backref=db.backref('team', lazy='dynamic'))
    matches = db.relationship('Match', backref='team', lazy='dynamic')

    def __repr__(self):
        return '<Team {}>'.format(self.team_num)


class ScoutingEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(16), db.ForeignKey('event.key'))
    team_number = db.Column(db.Integer, db.ForeignKey('team.number'))
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    value = db.Column(db.JSON)

    def __repr__(self):
        return '<ScoutingEntry {0}:{1} [{2}]>'.format(self.event, self.team_number, self.key)

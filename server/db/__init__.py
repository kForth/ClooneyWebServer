from flask_sqlalchemy import SQLAlchemy

from server import app, tba

sql_db = SQLAlchemy(app)


class DatabaseHelper:
    # Team

    def setup_team(self, number, update_tba=True):
        from server.db.models import Team
        team = Team.query.filter_by(number=number).first()

        if not team:
            team = Team(number=number)
            sql_db.session.add(team)

        if update_tba:
            try:
                team.info = tba.get_team_info(number)
            except Exception as ex:
                print(ex)
                print("Couldn't get tba info for team {}".format(number))

        sql_db.session.commit()
        return team

    def get_team(self, number, create_if_missing=True, update_tba_on_create=True):
        from server.db.models import Team
        team = Team.query.filter_by(number=number).first()
        if not team and create_if_missing:
            team = self.setup_team(number, update_tba_on_create)
        return team

    # Event

    def setup_event(self, event_key, update_tba=True):
        from server.db.models import Event
        event = Event.query.filter_by(key=event_key).first()

        if not event:
            event = Event(key=event_key, year=int(event_key[:4]))
            sql_db.session.add(event)

        if update_tba:
            try:
                event.info = tba.get_event_info(event_key)
            except Exception as ex:
                print(ex)
                print("Couldn't get tba info for event {}".format(event_key))

        sql_db.session.commit()
        return event

    def get_event(self, event_key, create_if_missing=True, update_tba_on_create=True):
        from server.db.models import Event
        event = Event.query.filter_by(key=event_key).first()
        if not event and create_if_missing:
            event = self.setup_event(event_key, update_tba_on_create)
        return event

    def setup_event_matches_from_tba(self, event_key):
        event = self.get_event(event_key)
        matches = tba.get_event_matches(event_key)
        for match_info in matches:
            match_level = match_info['comp_level']
            if match_level != 'qm':
                match_level += str(match_info['set_number'])

            match = self.get_match(event_key, match_level, match_info['match_number'],
                                   update_tba_on_create=False)
            match.info = match_info
            for alliance in match_info['alliances'].keys():
                for team in match_info['alliances'][alliance]['team_keys']:
                    match.add_team(self.get_team(int(team[3:])).number)

        return event

    def get_all_events(self):
        from server.db.models import Event
        return Event.query.all()

    def get_events_for_year(self, year):
        from server.db.models import Event
        return Event.query.filter_by(year=year).all()

    # Match

    def setup_match(self, event_key, match_level, match_number, update_tba=True):
        from server.db.models import Match

        match = Match.query.filter_by(event_key=event_key, match_number=match_number, match_level=match_level).first()

        if not match:
            match = Match(match_number=match_number, match_level=match_level, event_key=event_key)
            sql_db.session.add(match)

        if update_tba:
            try:
                match.info = tba.get_match_info(match.get_tba_key())
            except:
                print("Couldn't get tba info for match {}".format(match.get_tba_key()))
        sql_db.session.commit()
        return match

    def get_match(self, event_key, match_level, match_number, create_if_missing=True, update_tba_on_create=True):
        from server.db.models import Match
        match = Match.query.filter_by(event_key=event_key, match_number=match_number, match_level=match_level).first()
        if not match and create_if_missing:
            match = self.setup_match(event_key, match_level, match_number, update_tba_on_create)
        return match

    # Entry

    def setup_scouting_entry(self, event_key, team_number, match_level, match_number, data):
        from server.db.models import ScoutingEntry
        event = self.get_event(event_key)  # Create if missing.
        team = self.get_team(team_number)  # Create if missing.
        match = self.get_match(event_key, match_level, match_number)
        entry = self.get_scouting_entry(event_key, team_number, match_level, match_number)
        if not entry:
            entry = ScoutingEntry(event=event_key, team_number=team_number, match_id=match.id)
            sql_db.session.add(entry)

        if match.teams is None:
            match.teams = []
        match.teams = list(match.teams) + [team_number]

        entry.value = data
        sql_db.session.commit()
        return entry

    def get_scouting_entry(self, event_key, team_number, match_level, match_number):
        from server.db.models import ScoutingEntry
        match = self.get_match(event_key, match_level, match_number)
        if match:
            return ScoutingEntry.query.filter_by(event=event_key, team_number=team_number, match_id=match.id).first()
        return None

    def get_scouting_entries_for_team_at_event(self, event_key, team_number):
        from server.db.models import ScoutingEntry
        return ScoutingEntry.query.filter_by(event=event_key, team_number=team_number).all()

    def get_scouting_entries_for_match(self, event_key, match_level, match_number):
        from server.db.models import ScoutingEntry, Match
        match = self.get_match(event_key, match_level, match_number)
        return ScoutingEntry.query.filter_by(event=event_key, match_id=match.id).all()

    def get_scouting_entries_for_event(self, event_key):
        from server.db.models import ScoutingEntry
        return ScoutingEntry.query.filter_by(event=event_key).all()


if __name__ == "__main__":
    # from server.db import sql_db
    # from server.db.models import *
    # sql_db.create_all()

    db = DatabaseHelper()

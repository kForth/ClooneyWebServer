from flask_sqlalchemy import SQLAlchemy
from tba_py import TBA


class MatchPredictor:
    def __init__(self, tba: TBA, sql_db: SQLAlchemy):
        self.tba = tba
        self.sql_db = sql_db

    def process_event(self, event_id: str):
        from server.models import Event
        event = Event.query.filter_by(id=event_id).first()
        if not event:
            return
        opr_dict = self._get_opr_dict(event)
        matches = self.tba.get_event_matches(event_id)
        match_list = []
        for match in matches:
            if match['comp_level'] != 'qm':
                continue
            red_score = 0
            match['alliances']['red']['team_list'] = {}
            for i in range(len(match['alliances']['red']['team_keys'])):
                team = int(match['alliances']['red']['team_keys'][i][3:])
                match['alliances']['red']['team_list'][str(i+1)] = team
                red_score += opr_dict[team]
            blue_score = 0
            match['alliances']['blue']['team_list'] = {}
            for i in range(len(match['alliances']['blue']['team_keys'])):
                team = int(match['alliances']['blue']['team_keys'][i][3:])
                match['alliances']['blue']['team_list'][str(i+1)] = team
                blue_score += opr_dict[team]
            match['alliances']['red']['predict_score'] = int(red_score)
            match['alliances']['blue']['predict_score'] = int(blue_score)
            match_list.append(match)

        event.set_matches(match_list)
        sql_db.session.commit()

    @staticmethod
    def _get_opr_dict(event):
        from server.models import OprEntry
        teams = event.get_team_list()
        oprs = {}
        for team in teams:
            team_number = team['team_number']
            entries = OprEntry.query.filter_by(team=team_number, score_key="totalPoints").all()
            if entries:
                oprs[team_number] = round(max(map(lambda x: x.value, entries)), 2)
            else:
                oprs[team_number] = 0
        return oprs


if __name__ == "__main__":
    from server import sql_db
    mp = MatchPredictor(TBA('GdZrQUIjmwMZ3XVS622b6aVCh8CLbowJkCs5BmjJl2vxNuWivLz3Sf3PaqULUiZW'), sql_db)
    mp.process_event("2017oncmp")

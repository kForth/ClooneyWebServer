from datetime import datetime

import requests


class TBA(object):
    tba_url = "http://thebluealliance.com/api/v2"

    def __init__(self, user_id, app_description, app_version):
        self.user_id = user_id.replace(":", "-")
        self.app_description = app_description.replace(":", "-")
        self.app_version = app_version.replace(":", "-")
        self.headers = {'X-TBA-App-Id': self.user_id + ":" + self.app_description + ":v" + self.app_version}
        self._setup_methods()

    def _setup_methods(self):
        # Teams
        self.get_teams = lambda page_num: self._get("/teams/" + page_num)
        self.get_team = lambda team, suffix="": self._get("/team/frc{0}{1}".format(team, suffix))
        self.get_team_events = lambda team, year=datetime.now().year: self.get_team(team, "/{}/events".format(year))
        self.get_team_event_awards = lambda team, event_id: self.get_team(team, "/event/{}/awards".format(event_id))
        self.get_team_event_matches = lambda team, event_id: self.get_team(team, "/event/{}/matches".format(event_id))
        self.get_team_years_participated = lambda team: self.get_team(team, "/years_participated")
        self.get_team_media = lambda team, year: self.get_team(team, "/{}/media".format(year))
        self.get_team_media = lambda team: self.get_team(team, "/media")
        self.get_team_history_events = lambda team: self.get_team(team, "/history/events")
        self.get_team_history_awards = lambda team: self.get_team(team, "/history/awards")
        self.get_team_history_robots = lambda team: self.get_team(team, "/history/robots")
        self.get_team_history_districts = lambda team: self.get_team(team, "/history/districts")

        # Events
        self.get_events = lambda year=datetime.now().year: self._get("/events/{}".format(year))
        self.get_event = lambda event_id, suffix="": self._get("/event/{0}{1}".format(event_id, suffix))
        self.get_event_teams = lambda event_id: self.get_event(event_id, "/teams")
        self.get_event_matches = lambda event_id: self.get_event(event_id, "/matches")
        self.get_event_stats = lambda event_id: self.get_event(event_id, "/stats")
        self.get_event_rankings = lambda event_id: self.get_event(event_id, "/rankings")
        self.get_event_awards = lambda event_id: self.get_event(event_id, "/awards")
        self.get_event_district_points = lambda event_id: self.get_event(event_id, "/district_points")

        # Match
        # Example match_key: '2014cmp_f1m1'
        # Example match_key: '2014cmp_qm4'
        self.get_single_match = lambda match_key: self._get("/match/" + match_key)

        # District
        self._get_district = lambda id, year, suffix: self._get("/districts/{0}/{1}{2}".format(id, year, suffix))
        self.get_districts = lambda year=datetime.now().year: self._get("/districts/{}".format(year))
        self.get_district_events = lambda district_id, year: self._get_district(district_id, year, "/events")
        self.get_district_rankings = lambda district_id, year: self._get_district(district_id, year, "/rankings")
        self.get_district_teams = lambda district_id, year: self._get_district(district_id, year, "/teams")

    def _get(self, url):
        result = requests.get(self.tba_url + url, headers=self.headers)
        if result.status_code == 200:
            return result.json()
        else:
            raise BadResponseCodeException("Bad Response Code: {}".format(result.status_code))


class BadResponseCodeException(Exception):
    pass






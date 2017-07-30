import requests


class TBA(object):
    tba_url = 'http://thebluealliance.com/api/v3'

    def __init__(self, auth_key):
        self.auth_key = auth_key
        self.headers = {'X-TBA-Auth-Key': self.auth_key}
        self._setup_methods()

    def _setup_methods(self):
        # Teams
        self._get_team = lambda team, suffix='': self._get('/team/frc{0}{1}'.format(team, suffix))

        self.get_teams = lambda page_num, year='': self._get('/teams/{0}{1}{2}'.format(year, '/' if year else '', page_num))
        self.get_teams_simple = lambda page_num, year='': self._get('/teams/{0}{1}{2}/simple'.format(year, '/' if year else '', page_num))
        self.get_teams_keys = lambda page_num, year='': self._get('/teams/{0}{1}{2}/keys'.format(year, '/' if year else '', page_num))

        self.get_team_info = lambda team: self._get_team(team)
        self.get_team_info_simple = lambda team: self._get_team(team, '/simple')

        self.get_team_years_participated = lambda team: self._get_team(team, '/years_participated')
        self.get_team_districts = lambda team: self._get_team(team, '/districts')
        self.get_team_robots = lambda team: self._get_team(team, '/robots')

        self.get_team_events = lambda team, year='': self._get_team(team, '/events{0}{1}'.format('/' if year else'', year))
        self.get_team_events_simple = lambda team, year='': self._get_team(team, '/events{0}{1}/simple'.format('/' if year else'', year))
        self.get_team_events_keys = lambda team, year='': self._get_team(team, '/events{0}{1}/keys'.format('/' if year else'', year))

        self.get_team_event_matches = lambda team, event_id: self._get_team(team, '/event/{}/matches'.format(event_id))
        self.get_team_event_matches_simple = lambda team, event_id: self._get_team(team, '/event/{}/matches/simple'.format(event_id))
        self.get_team_event_matches_keys = lambda team, event_id: self._get_team(team, '/event/{}/matches/keys'.format(event_id))

        self.get_team_event_awards = lambda team, event_id: self._get_team(team, '/event/{}/awards'.format(event_id))
        self.get_team_event_status = lambda team, event_id: self._get_team(team, '/event/{}/status'.format(event_id))

        self.get_team_awards = lambda team, year='': self._get_team(team, '/awards{0}{1}'.format('/' if year else '', year))

        self.get_team_matches = lambda team, year: self._get_team(team, '/matches/{0}'.format(year))
        self.get_team_matches_simple = lambda team, year: self._get_team(team, '/matches/{}/simple'.format(year))
        self.get_team_matches_keys = lambda team, year: self._get_team(team, '/matches/{}/keys'.format(year))

        self.get_team_media = lambda team, year: self._get_team(team, '/media/{}'.format(year))
        self.get_team_social_media = lambda team: self._get_team(team, '/social_media')

        # Events
        self._get_event = lambda event_id, suffix='': self._get('/event/{0}{1}'.format(event_id, suffix))

        self.get_events = lambda year: self._get('/events/{}'.format(year))
        self.get_events_simple = lambda year: self._get('/events/{}/simple'.format(year))
        self.get_events_keys = lambda year: self._get('/events/{}/keys'.format(year))

        self.get_event_info = lambda event_id: self._get_event(event_id)
        self.get_event_info_simple = lambda event_id: self._get_event(event_id, '/simple')

        self.get_event_alliances = lambda event_id: self._get_event(event_id, '/alliances')
        self.get_event_insights = lambda event_id: self._get_event(event_id, '/insights')
        self.get_event_oprs = lambda event_id: self._get_event(event_id, '/oprs')
        self.get_event_predictions = lambda event_id: self._get_event(event_id, '/predictions')
        self.get_event_rankings = lambda event_id: self._get_event(event_id, '/rankings')
        self.get_event_district_points = lambda event_id: self._get_event(event_id, '/district_points')
        self.get_event_awards = lambda event_id: self._get_event(event_id, '/awards')

        self.get_event_teams = lambda event_id: self._get_event(event_id, '/teams')
        self.get_event_teams_simple = lambda event_id: self._get_event(event_id, '/teams/simple')
        self.get_event_teams_keys = lambda event_id: self._get_event(event_id, '/teams/keys')

        self.get_event_matches = lambda event_id: self._get_event(event_id, '/matches')
        self.get_event_matches_simple = lambda event_id: self._get_event(event_id, '/matches/simple')
        self.get_event_matches_keys = lambda event_id: self._get_event(event_id, '/matches/keys')

        # Match
        self.get_match_info = lambda match_key: self._get('/match/' + match_key)
        self.get_match_info_simple = lambda match_key: self._get('/match/' + match_key)

        # District
        self._get_district = lambda id, suffix: self._get('/districts/{0}{1}'.format(id, suffix))

        self.get_districts = lambda year: self._get('/districts/{}'.format(year))

        self.get_district_events = lambda district_id: self._get_district(district_id, '/events')
        self.get_district_events_simple = lambda district_id: self._get_district(district_id, '/events/simple')
        self.get_district_events_keys = lambda district_id: self._get_district(district_id, '/events/keys')

        self.get_district_teams = lambda district_id: self._get_district(district_id, '/teams')
        self.get_district_teams_simple = lambda district_id: self._get_district(district_id, '/teams/simple')
        self.get_district_teams_keys = lambda district_id: self._get_district(district_id, '/teams/keys')

        self.get_district_rankings = lambda district_id: self._get_district(district_id, '/rankings')

    def _get(self, url):
        result = requests.get(self.tba_url + url, headers=self.headers)
        if result.status_code == 200:
            return result.json()
        else:
            raise BadResponseCodeException('Bad Response Code: {}'.format(result.status_code))


class BadResponseCodeException(Exception):
    pass

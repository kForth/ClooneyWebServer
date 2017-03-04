from tba_py import BlueAllianceAPI
from flask import make_response, jsonify, request

from datetime import datetime

from server.db import Database
from util.runners import Runner


class InfoServer(object):
    def __init__(self, add: classmethod, db: Database, tba: BlueAllianceAPI, url_prefix=""):
        self._add = lambda *x, **y: add(*x, **y, url_prefix=url_prefix)
        self.db = db
        self.tba = tba
        self._register_views()

    def _register_views(self):
        self._add('/events', self.get_available_events)
        self._add('/events/<int:year>', self.get_available_events)
        self._add('/event/<event_id>/info', self.get_event_info)
        self._add('/event/<event_id>/teams', self.get_event_teams)
        self._add('/event/<event_id>/matches/<level>', self.get_matches)
        self._add('/event/<event_id>/matches', self.get_matches)
        self._add('/setup/<event_id>', self.trigger_event_setup, methods=['POST'])

    def get_event_info(self, event_id):
        return make_response(jsonify(self.db.get_event_info(event_id)))

    def get_matches(self, event_id, level=None):
        matches = []
        for match in self.tba.get_event_matches(event_id):
            if level is None or level.lower() == match["comp_level"].lower():
                for alli in ["red", "blue"]:
                    teams = match['alliances'][alli]['teams']
                    match['alliances'][alli]['teams'] = {}
                    for i in range(len(teams)):
                        match['alliances'][alli]['teams'][str(i + 1)] = int(teams[i][3:])
                    if match not in matches:
                        matches.append(match)
        print(matches[0]["alliances"]["red"]["teams"]["1"])
        return make_response(jsonify(matches))

    def get_available_events(self, year=None):
        events = self.db._get_events()
        event_list = []
        for key in events.keys():
            if year is None or str(year) in key:
                event_name = key
                if "tba" in events[key].keys():
                    event_name = "{0} {1}".format(key[:4], events[key]["tba"]["short_name"])
                event_list.append({
                    "id":   key,
                    "name": event_name
                })
        return make_response(jsonify(event_list))

    def get_event_teams(self, event_id):
        team_info = self.db.get_event_info(event_id)["teams"]
        return make_response(jsonify(team_info), 200)

    def setup_event_teams(self, event_id):
        print("Updating Event: {}... Updating teams".format(event_id))
        event_info = self.db.get_event_info(event_id)
        team_list = self.tba.get_event_teams(event_id)
        event_start_date = datetime.strptime(event_info["tba"]["start_date"], "%Y-%m-%d")
        for team_info in team_list:
            events = self.tba.get_team_events(str(team_info["team_number"]), "2017")
            team_info["prev_events"] = 0
            for event in events:
                if datetime.strptime(event["start_date"], "%Y-%m-%d") < event_start_date:
                    team_info["prev_events"] += 1
        event_info["teams"] = team_list
        self.db.set_event_info(event_id, event_info)

    def setup_event(self, event_id, info):
        print("Updating Event: {}".format(event_id))
        try:
            info["tba"] = self.tba.get_event(event_id)
        except:
            print("Updating Event: {}... Couldn't get TBA info.".format(event_id))
            pass
        self.db.add_event(event_id, info)
        self.setup_event_teams(event_id)
        print("Updating Event: {}... Done".format(event_id))

    def trigger_event_setup(self, event_id):
        if len(event_id) > 0 and request.is_json:
            info = request.json
            Runner(lambda: self.setup_event(event_id, info)).run()
        return make_response(jsonify(), 200)

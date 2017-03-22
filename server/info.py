from tba_py import BlueAllianceAPI
from flask import make_response, jsonify, request

from datetime import datetime
from glob import glob
from os import path
import json

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
        self._add('/event/<event_id>/team/<int:team_number>', self.get_team_info)
        self._add('/event/<event_id>/team/<int:team_number>/images', self.get_team_images)
        self._add('/event/<event_id>/matches/<level>/<int:team_number>', self.get_matches)
        self._add('/event/<event_id>/matches/<level>', self.get_matches)
        self._add('/event/<event_id>/matches', self.get_matches)
        self._add('/setup/<event_id>', self.trigger_event_setup, methods=['POST'])

    def get_team_info(self, event_id, team_number):
        event_info = self.db.get_event_info(event_id)["teams"]
        for line in event_info:
            if str(line["team_number"]) == str(team_number):
                team_info = line
                break
        else:
            return make_response(jsonify([]), 400)
        return make_response(jsonify(team_info))

    @staticmethod
    def get_team_images(event_id, team_number):
        images = []
        file_types = ["jpg", "png", "gif", "jpeg", "JPG", "PNG", "GIF", "JPEG"]
        if path.isdir("server/static/robot_pics/" + event_id + "/" + str(team_number)):
            for file_type in file_types:
                images += glob("server/static/robot_pics/{0}/{1}/*.{2}".format(event_id, team_number, file_type))
        images = list(map(lambda x: x.split("/")[-1], images))
        return make_response(jsonify(images))

    def get_event_info(self, event_id):
        return make_response(jsonify(self.db.get_event_info(event_id)))

    def get_matches(self, event_id, level=None, team_number=None):
        headers = self.db.get_table_headers(event_id, 'matches')
        lines = []
        for match in self.tba.get_event_matches(event_id):
            if level is None or level.lower() == match["comp_level"].lower():
                teams = {}
                for alli in ["red", "blue"]:
                    teams[alli] = match['alliances'][alli]['teams']
                    match['alliances'][alli]['teams'] = dict(zip(map(str, range(1, len(teams[alli])+1)), map(lambda x: x[3:], teams[alli])))
                if team_number is None or team_number in teams["red"] + teams["blue"]:
                    line = {}
                    for header in headers:
                        line[header["sort_id"]] = self._get_data(match, header["key"])
                    lines.append(line)
        return make_response(jsonify(lines))

    def get_available_events(self, year=None):
        events = self.db.get_events()
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
        table_data = self._create_table_data(self.db.get_table_headers(event_id, "teams"), team_info)
        return make_response(jsonify(table_data), 200)

    def setup_event_teams(self, event_id):
        print("Updating Event: {}... Updating teams".format(event_id))
        event_info = self.db.get_event_info(event_id)
        team_list = self.tba.get_event_teams(event_id)
        event_start_date = datetime.strptime(event_info["tba"]["start_date"], "%Y-%m-%d")
        for team_info in team_list:
            events = self.tba.get_team_events(str(team_info["team_number"]), "2017")
            team_info["num_events"] = len(events)
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

    def _create_table_data(self, headers, data):
        table_data = []
        for elem in data:
            line = {}
            for header in headers:
                line[header['sort_id']] = self._get_data(elem, header['key'])
            table_data.append(line)
        return table_data

    def _get_data(self, data, key):
        if type(key) is str:
            key = key.split(",")
        val = data
        for k in key:
            val = val[str(k).strip()]
        return val

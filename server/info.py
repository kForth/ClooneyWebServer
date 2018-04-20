import json
from datetime import datetime
from glob import glob
from os import path

from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy

from server.db import Database
from tba_py import TBA
from util.runners import Runner


class InfoServer(object):
    def __init__(self, add: classmethod, db: Database, sql_db: SQLAlchemy, tba: TBA, url_prefix="", path_prefix=""):
        self._add = lambda *x, **y: add(*x, url_prefix=url_prefix, **y)
        self.db = db
        self.sql_db = sql_db
        self.tba = tba
        self.path_prefix = path_prefix
        self._register_views()

    def _register_views(self):
        self._add('/events', self.get_available_events)
        self._add('/events/<int:year>', self.get_available_events)
        self._add('/event/<event_id>/info', self.get_event_info)
        self._add('/event/<event_id>/teams', self.get_event_teams)
        self._add('/event/<event_id>/team/<int:team_number>', self.get_team_info)
        self._add('/event/<event_id>/team/<int:team_number>/images', self.get_team_images)
        self._add('/event/<event_id>/team_images', self.get_team_images_for_event)
        self._add('/event/<event_id>/matches/<level>/<int:team_number>', self.get_matches)
        self._add('/event/<event_id>/matches/<level>', self.get_matches)
        self._add('/event/<event_id>/matches', self.get_matches)
        self._add('/event/<event_id>/match/<key>', self.get_match)
        self._add('/setups/<event_id>', self.trigger_event_setup, methods=['POST'])

    def get_team_info(self, event_id, team_number):
        from server.models import Event
        event_info = Event.query.filter_by(id=event_id).first()
        if event_info:
            event_info = event_info.get_team_list()
            for line in event_info:
                if str(line["team_number"]) == str(team_number):
                    team_info = line
                    break
            else:
                return jsonify([]), 400
            return jsonify(team_info)
        else:
            return jsonify([]), 400

    def get_team_images_for_event(self, event_id):
        from server.models import Event
        images = {}
        file_types = ["jpg", "png", "gif", "jpeg"]
        teams = Event.query.filter_by(id=event_id).first().get_team_list()
        for team in teams:
            team_number = str(team['team_number'])
            if path.isdir(self.path_prefix + "server/static/robot_pics/" + str(team_number)):
                images[team_number] = []
                for file_type in file_types + [e.upper() for e in file_types]:
                    img_paths = glob(self.path_prefix + "server/static/robot_pics/{0}/*.{1}".format(team_number, file_type))
                    img_names = list(map(lambda x: x.split("/")[-1], img_paths))
                    images[team_number] += img_names
        return jsonify(images)

    def get_team_images(self, event_id, team_number):
        images = []
        file_types = ["jpg", "png", "gif", "jpeg"]
        if path.isdir(self.path_prefix + "server/static/robot_pics/" + str(team_number)):
            for file_type in file_types + [e.upper() for e in file_types]:
                images += glob(self.path_prefix + "server/static/robot_pics/{0}/*.{1}".format(team_number, file_type))
        images = list(map(lambda x: x.split("/")[-1], images))
        return jsonify(images)

    def get_event_info(self, event_id):
        from server.models import Event
        event_info = Event.query.filter_by(id=event_id).first().get_tba_info()
        return jsonify(event_info)

    def get_match(self, event_id, key):
        match = self.tba.get_match_info(event_id + "_" + key)
        return jsonify(match)

    def get_matches(self, event_id, level=None, team_number=None):
        lines = []
        for match in self.tba.get_event_matches(event_id):
            match["short_key"] = match["key"].split("_")[-1]
            if level is None or str(level).lower() == match["comp_level"].lower():
                teams = {}
                for alli in ["red", "blue"]:
                    teams[alli] = match['alliances'][alli]['team_keys']
                    match['alliances'][alli]['teams'] = dict(
                        zip(map(str, range(1, len(teams[alli]) + 1)), map(lambda x: x[3:], teams[alli])))
                if team_number is None or team_number in teams["red"] + teams["blue"]:
                    lines.append(match)
        return jsonify(lines)

    def get_available_events(self, year=None):
        if 'If-Modified-Since' in request.headers:
            last_modified_date = self.db.get_event_list_last_modified()
            header_date = datetime.strptime(request.headers['If-Modified-Since'], '%Y-%m-%dT%H:%M:%S.%fZ')
            if last_modified_date < header_date:
                return "", 304

        from server.models import Event
        events = Event.query.all()
        event_list = []
        for e in events:
            key = e.id
            if year is None or str(year) in key:
                if e.get_tba_info() is not None:
                    event_name = "{0} {1}".format(key[:4], e.get_tba_info()["short_name"])
                else:
                    event_name = key
                event_list.append({
                    "id":   key,
                    "name": event_name
                })
        return jsonify(event_list)

    def get_event_teams(self, event_id):
        if 'If-Modified-Since' in request.headers:
            last_modified_date = self.db.get_event_last_modified(event_id)
            header_date = datetime.strptime(request.headers['If-Modified-Since'], '%Y-%m-%dT%H:%M:%S.%fZ')
            if last_modified_date < header_date:
                return "", 304
        from server.models import Event
        team_info = Event.query.filter_by(id=event_id).first().get_team_list()
        return jsonify(team_info), 200

    def get_teams_for_event(self, entry):
        print("Updating Event: {}... Updating teams".format(entry.id))
        event_info = entry.get_tba_info()
        team_list = self.tba.get_event_teams(entry.id)
        event_start_date = datetime.strptime(event_info["start_date"], "%Y-%m-%d")
        for team_info in team_list:
            events = self.tba.get_team_events(str(team_info["team_number"]), "2018")
            team_info["num_events"] = len(events)
            team_info["prev_events"] = 0
            for event in events:
                if datetime.strptime(event["start_date"], "%Y-%m-%d") < event_start_date:
                    team_info["prev_events"] += 1
        entry.set_team_list(team_list)
        self.sql_db.session.commit()

    def setup_event(self, event_id):
        print("Updating Event: {}".format(event_id))
        from server.models import Event
        tba_info = self.tba.get_event_info(event_id)
        entry = Event.query.filter_by(id=event_id).first()
        if entry:
            entry.set_tba_info(tba_info)
            self.sql_db.session.commit()
        else:
            entry = Event(event_id, tba_info, [], [])
            self.sql_db.session.add(entry)
            self.sql_db.session.commit()

        self.get_teams_for_event(entry)
        filename = 'clooney/{0}/{1}.json'
        json.dump(json.load(open(filename.format('analysis', 'default' + event_id[:4]))), open(filename.format('analysis', event_id), 'w+'))
        json.dump(json.load(open(filename.format('expressions', 'default' + event_id[:4]))), open(filename.format('expressions', event_id), 'w+'))
        json.dump(json.load(open(filename.format('headers', 'default' + event_id[:4]))), open(filename.format('headers', event_id), 'w+'))

        from server.models import LastModifiedEntry
        event_list_entry = LastModifiedEntry.query.filter_by(event=event_id, key='event_list').first()
        if not event_list_entry:
            event_list_entry = LastModifiedEntry(event=event_id, key='event_list')
            self.sql_db.session.add(event_list_entry)
        event_list_entry.last_modified = datetime.utcnow()

        event_entry = LastModifiedEntry.query.filter_by(event=event_id, key='event').first()
        if not event_entry:
            event_entry = LastModifiedEntry(event=event_id, key='event')
            self.sql_db.session.add(event_entry)
        event_entry.last_modified = datetime.utcnow()
        self.sql_db.session.commit()

        print("Updating Event: {}... Done".format(event_id))

    def trigger_event_setup(self, event_id):
        if len(event_id) > 0:
            Runner(lambda: self.setup_event(event_id)).run()
        return jsonify(), 200

    def _get_data(self, data, key):
        keys = key
        if type(key) is str:
            keys = []
            for k in key.split(","):
                for l in k.split("."):
                    keys.append(l)
        val = data
        for k in keys:
            val = val[str(k).strip()]
        return val

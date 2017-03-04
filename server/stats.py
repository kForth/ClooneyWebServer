import json
from os import path

from flask import jsonify, make_response, request
from tba_py import BlueAllianceAPI
from tinydb import TinyDB
from server.db import Database


class StatsServer(object):
    def __init__(self, add: classmethod, db: Database, tba: BlueAllianceAPI, url_prefix=""):
        self._add = lambda *x, **y: add(*x, **y, url_prefix=url_prefix)
        self.db = db
        self.tba = tba
        self._register_views()

    def _get_event_db(self, event):
        return TinyDB("db/events/{}.json".format(event))

    def _register_views(self):
        self._add('/event/<event_id>/oprs', self.get_event_opr)
        self._add('/event/<event_id>/stats/avg/<int:team_number>', self.get_team_stats_avg)
        self._add('/event/<event_id>/stats/avg', self.get_event_stats_avg)
        self._add('/event/<event_id>/stats/raw', self.get_event_stats_raw)
        self._add('/event/<event_id>/pit', self.get_event_pit_data)
        self._add('/event/<event>/expressions', self.get_expressions, methods=['GET', 'POST'])
        self._add('/team/<team_number>/info/', self.get_team_info)

    def get_event_opr(self, event_id):
        return make_response(jsonify(self.db.get_event_oprs(event_id)))

    def get_event_stats_avg(self, event_id):
        return make_response(jsonify(self.__get_avg_data(event_id)))

    def get_event_stats_raw(self, event_id):
        return make_response(jsonify(self.__get_raw_data(event_id)))

    def get_event_pit_data(self, event_id):
        return make_response(jsonify(self.__get_pit_scouting(event_id)))

    def get_team_stats_avg(self, event_id, team_number):
        return make_response(jsonify(self.__get_avg_data(event_id)[team_number]))

    def get_team_info(self, team_number):
        return make_response(jsonify(self.tba.get_team(team_number)))

    def get_expressions(self, event):
        file_path = 'clooney/expressions/{}.json'.format(event)
        if request.method == "GET":
            expressions = json.load(open(file_path))
            return make_response(jsonify(list(expressions)))
        if request.method == "POST":
            expressions = request.json
            json.dump(expressions, open(file_path, "w+"))
            # process_event(event)  # TODO
            return make_response(jsonify({}), 200)

    def __get_raw_data(self, event_id):
        fp = "clooney/data/{}/raw_data.json".format(event_id)
        return self.__get_file(fp) if event_id != "undefined" else []

    def __get_avg_data(self, event_id):
        fp = "clooney/data/{}/avg_data.json".format(event_id)
        return self.__get_file(fp) if event_id != "undefined" else []

    def __get_calculated_data(self, event_id):
        fp = "clooney/data/{}/calculated.json".format(event_id)
        return self.__get_file(fp) if event_id != "undefined" else []

    def __get_pit_scouting(self, event_id):
        fp = "clooney/data/{}/pit_scout.json".format(event_id)
        return self.__get_file(fp) if event_id != "undefined" else []

    def __get_file(self, fp):
        if not path.isfile(fp):
            return []
        return json.load(open(fp))

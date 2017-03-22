import json

from flask import jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from tba_py import BlueAllianceAPI
from tinydb import TinyDB

from server.db import Database


class StatsServer(object):
    def __init__(self, add: classmethod, db: Database, sql_db: SQLAlchemy, tba: BlueAllianceAPI, url_prefix=""):
        self._add = lambda *x, **y: add(*x, **y, url_prefix=url_prefix)
        self.db = db
        self.sql_db = sql_db
        self.tba = tba
        self._register_views()

    def _get_event_db(self, event):
        return TinyDB("db/events/{}.json".format(event))

    def _register_views(self):
        self._add('/event/<event_id>/stats/avg', self.get_event_stats_avg)
        self._add('/event/<event_id>/stats/raw', self.get_event_stats_raw)
        self._add('/event/<event_id>/stats/avg/<int:team_number>', self.get_team_stats_avg)
        self._add('/event/<event_id>/stats/raw/<int:team_number>', self.get_team_stats_raw)
        self._add('/event/<event_id>/pit', self.get_event_pit_data)
        self._add('/event/<event_id>/oprs', self.get_best_oprs)
        self._add('/event/<event>/expressions', self.get_expressions, methods=['GET', 'POST'])

    def get_best_oprs(self, event_id):
        from server.models import OprEntry
        headers = self.db.get_table_headers(event_id, "oprs")
        teams = list(map(lambda x: x["team_number"], self.db.get_event_info(event_id)["teams"]))
        data = []
        for team in teams:
            line = {
                'a': team
            }
            for header in headers:
                if header["title"] == "Team":
                    continue
                entries = OprEntry.query.filter_by(team=team, score_key=header["key"]).all()
                if entries:
                    line[header["sort_id"]] = round(max(map(lambda x: x.value, entries)), 2)
                else:
                    line[header["sort_id"]] = 0
            data.append(line)
        return make_response(jsonify(data))

    def get_event_stats_avg(self, event_id):
        data = self.db.get_avg_data(event_id).values()
        table_data = self._create_table_data(self.db.get_table_headers(event_id, "stats_avg"), data, True)
        print(table_data)
        return make_response(jsonify(table_data))

    def get_event_stats_raw(self, event_id):
        from server.models import ScoutingEntry
        entries = list(map(lambda x: x.to_dict()["data"], ScoutingEntry.query.filter_by(event=event_id).all()))
        table_data = self._create_table_data(self.db.get_table_headers(event_id, "stats_raw"), entries)
        return make_response(jsonify(table_data))

    def get_event_pit_data(self, event_id):
        data = self.db.get_pit_scouting(event_id)
        table_data = self._create_table_data(self.db.get_table_headers(event_id, "pit_data"), data)
        return make_response(jsonify(table_data))

    def get_team_stats_avg(self, event_id, team_number):
        data = self.db.get_avg_data(event_id)[str(team_number)]
        return make_response(jsonify(data))

    def get_team_stats_raw(self, event_id, team_number):
        data = self.db.get_raw_data(event_id)
        output = []
        for line in data:
            if str(line["team_number"]) == str(team_number):
                output.append(line)
        table_data = self._create_table_data(self.db.get_table_headers(event_id, "single_team_data"), output)
        return make_response(jsonify(table_data))

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

    def _create_table_data(self, headers, data, tooltip=False):
        table_data = []
        for elem in data:
            line = {}
            for header in headers:
                line[header['sort_id']] = self._get_data(elem, header['key'])
                if tooltip:
                    line[header['sort_id'] + 'tooltip'] = ",".join(
                        map(str, self._get_data(elem, header['key'].split(",")[:-1] + ["raw"])))
            table_data.append(line)
        return table_data

    @staticmethod
    def _get_data(data, key):
        if type(key) is str:
            key = key.split(",")
        val = data
        for k in key:
            val = val[k.strip()]
        return val

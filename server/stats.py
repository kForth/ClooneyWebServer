import json

from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy

from predict.opr import OprCalculator
from server.db import Database
from server.generator import SpreadsheetGenerator
from tba_py import TBA
from updaters import AverageCalculator
import datetime

from util.runners import TriggeredPeriodicRunner


class StatsServer(object):
    def __init__(self, add: classmethod, db: Database, sql_db: SQLAlchemy, tba: TBA, url_prefix="", path_prefix=""):
        self._add = lambda *x, **y: add(*x, url_prefix=url_prefix, **y)
        self.db = db
        self.sql_db = sql_db
        self.tba = tba
        self._register_views()
        self.avg_calc = AverageCalculator(sql_db, db, path_prefix)
        self.opr_calc = OprCalculator(tba)
        self.events_to_update = []
        self.event_updater = TriggeredPeriodicRunner(self.update_events, auto_start=False, period=20)
        self.spreadsheet_gen = SpreadsheetGenerator(sql_db, tba, path_prefix)

    def _register_views(self):
        self._add('/event/<event_id>/stats/avg/best', self.get_event_stats_avg_best)
        self._add('/event/<event_id>/stats/avg', self.get_event_stats_avg)
        self._add('/event/<event_id>/avg', self.get_event_avg)
        self._add('/event/<event_id>/stats/raw', self.get_event_stats_raw)
        self._add('/event/<event_id>/stats/avg/<int:team_number>', self.get_team_stats_avg)
        self._add('/event/<event_id>/stats/raw/<int:team_number>', self.get_team_stats_raw)
        self._add('/event/<event_id>/pit', self.get_event_pit_data)
        self._add('/event/<event_id>/oprs', self.get_best_oprs)
        self._add('/event/<event_id>/event_oprs', self.get_event_oprs)
        self._add('/event/<event_id>/predictions/<int:team_number>', self.get_match_predictions)
        self._add('/event/<event_id>/predictions', self.get_match_predictions)
        self._add('/event/<event>/expressions', self.get_expressions, methods=['GET', 'POST'])
        self._add('/event/<event>/update', self.trigger_event_update, methods=['GET'])
        self._add('/add_entry', self.add_scouting_entry, methods=["POST"])

    def update_events(self):
        for event in self.events_to_update:
            self.update_event(event)
            filename = "Clooney_{}.xlsx".format(event)
            google_filename = "Clooney {}".format(event.title())
            self.spreadsheet_gen.create_spreadsheet_for_event(event, filename=filename)
            self.spreadsheet_gen.upload_to_google_drive(filename, upload_filename=google_filename)
            print("updated {}".format(event))
        self.events_to_update = []

    def trigger_event_update(self, event):
        print("update")
        if event not in self.events_to_update:
            self.events_to_update.append(event)
            self.event_updater.start()
        return "", 200

    def update_event(self, event):
        self.avg_calc.update(event)
        from server.models import LastModifiedEntry
        entry = LastModifiedEntry.query.filter_by(event=event, key='stats').first()
        if not entry:
            entry = LastModifiedEntry(event=event, key='stats')
            self.sql_db.session.add(entry)
        entry.last_modified = datetime.datetime.utcnow()
        self.sql_db.session.commit()
        # self.opr_calc.get_event_oprs(event, db=self.sql_db)
        return ""

    def add_scouting_entry(self):
        from server.models import ScoutingEntry, LastModifiedEntry
        data = request.json
        data["data"] = json.dumps(data["data"])
        event = data["event"]

        last_modified_entry = LastModifiedEntry.query.filter_by(event=event, key='raw').first()
        if not last_modified_entry:
            last_modified_entry = LastModifiedEntry(event=event, key='raw')
            self.sql_db.session.add(last_modified_entry)
        last_modified_entry.last_modified = datetime.datetime.utcnow()
        self.sql_db.session.commit()

        try:
            entry = ScoutingEntry.query.filter_by(id=data['id']).first()
            if entry:
                entry.update(**data)
            else:
                raise KeyError('ID Not found in DB')
        except KeyError as _:
            if 'id' in data.keys():
                del data['id']
            entry = ScoutingEntry(**data)
            self.sql_db.session.add(entry)
        self.sql_db.session.commit()
        if event not in self.events_to_update:
            self.events_to_update.append(event)
            self.event_updater.start()
        return jsonify({'id': entry.id}), 200

    def get_match_predictions(self, event_id, team_number=None):
        from server.models import Event
        event = Event.query.filter_by(id=event_id).first()
        matches = event.get_matches()
        if event and matches:
            if team_number:
                match_list = []
                for match in matches:
                    if team_number in match['alliances']['red']['team_list'].values() or team_number in \
                            match['alliances']['blue']['team_list'].values():
                        match_list.append(match)
                matches = match_list
        return jsonify(matches)

    def get_best_oprs(self, event_id):
        if 'If-Modified-Since' in request.headers:
            last_modified_date = self.db.get_opr_last_modified()
            header_date = datetime.datetime.strptime(request.headers['If-Modified-Since'], '%Y-%m-%dT%H:%M:%S.%fZ')
            if last_modified_date < header_date:
                return "", 304
        from server.models import OprEntry, Event
        headers = self.db.get_table_headers(event_id, "oprs")
        event = Event.query.filter_by(id=event_id).first()
        teams = list(map(lambda x: x["team_number"], event.get_team_list()))
        data = []
        for team in teams:
            line = {
                'team_number': team
            }
            for header in headers:
                if header["title"] == "Team":
                    continue
                entries = OprEntry.query.filter_by(team=team, score_key=header["key"]).all()
                if entries:
                    line[header["key"]] = round(max(map(lambda x: x.value, entries)), 2)
                else:
                    line[header["key"]] = 0
            data.append(line)
        return jsonify(data)

    def get_event_oprs(self, event_id):
        if 'If-Modified-Since' in request.headers:
            last_modified_date = self.db.get_opr_last_modified()
            header_date = datetime.datetime.strptime(request.headers['If-Modified-Since'], '%Y-%m-%dT%H:%M:%S.%fZ')
            if last_modified_date < header_date:
                return "", 304
        from server.models import OprEntry, Event
        headers = self.db.get_table_headers(event_id, "oprs")
        event = Event.query.filter_by(id=event_id).first()
        teams = list(map(lambda x: x["team_number"], event.get_team_list()))
        data = []
        for team in teams:
            line = {
                'team_number': team
            }
            for header in headers:
                if header["title"] == "Team":
                    continue
                entries = OprEntry.query.filter_by(team=team, score_key=header["key"], event=event_id).all()
                if entries:
                    line[header["key"]] = round(max(map(lambda x: x.value, entries)), 2)
                else:
                    line[header["key"]] = 0
            data.append(line)
        return jsonify(data)

    def get_event_stats_avg(self, event_id):
        if 'If-Modified-Since' in request.headers:
            last_modified_date = self.db.get_stats_last_modified(event_id)
            header_date = datetime.datetime.strptime(request.headers['If-Modified-Since'], '%Y-%m-%dT%H:%M:%S.%fZ')
            if last_modified_date < header_date:
                return "", 304
        data = list(self.db.get_stats(event_id).values())
        return jsonify(data)

    def get_event_avg(self, event_id):
        data = list(self.db.get_avg_data(event_id).values())
        return jsonify(data)

    def get_event_stats_avg_best(self, event_id):
        data = list(self.db.get_avg_data(event_id).values())
        return jsonify(data)

    def get_event_stats_raw(self, event_id):
        if 'If-Modified-Since' in request.headers:
            last_modified_date = self.db.get_raw_last_modified(event_id)
            header_date = datetime.datetime.strptime(request.headers['If-Modified-Since'], '%Y-%m-%dT%H:%M:%S.%fZ')
            if last_modified_date < header_date:
                return "", 304
        from server.models import ScoutingEntry
        entries = list(map(lambda x: x.to_dict()["data"], ScoutingEntry.query.filter_by(event=event_id).all()))
        return jsonify(entries)

    def get_event_pit_data(self, event_id):
        data = self.db.get_pit_scouting(event_id)
        return jsonify(data)

    def get_team_stats_avg(self, event_id, team_number):
        data = self.db.get_avg_data(event_id)[str(team_number)]
        return jsonify(data)

    def get_team_stats_raw(self, event_id, team_number):
        data = self.db.get_raw_data(event_id)
        output = []
        for line in data:
            if str(line["team_number"]) == str(team_number):
                output.append(line)
        return jsonify(output)

    def get_expressions(self, event):
        file_path = 'clooney/expressions/{}.json'.format(event)
        if request.method == "GET":
            expressions = json.load(open(file_path))
            return jsonify(list(expressions))
        if request.method == "POST":
            expressions = request.json
            json.dump(expressions, open(file_path, "w+"))
            # process_event(event)  # TODO
            return jsonify({}), 200

    @staticmethod
    def _get_data(data, key, parent=False):
        if not key:
            return ""
        if type(key) is str:
            key = key.split(",")
        val = data
        for k in key:
            if parent and k is key[-1]:
                return val
            try:
                val = val[k.strip()]
            except KeyError:
                val = ""
                break
        return val

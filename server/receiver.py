import json

from flask import abort, jsonify, make_response, request

from server.db import Database
from updaters import AverageCalculator


class ReceiverServer(object):
    def __init__(self, add: classmethod, db: Database, url_prefix=""):
        self._add = lambda *args, **kwarg: add(*args, **kwarg, url_prefix=url_prefix)
        self.db = db
        self._register_views()

    def __update_event(self, event_id):
        try:
            AverageCalculator().update(event_id)
        except:
            pass

    def _register_views(self):
        self._add('/add/single/<event>', self.add_match, methods=['POST'])
        self._add('/add/bulk/<event>', self.add_matches, methods=['POST'])

    def _add_match(self, event, data):
        fp = 'clooney/data/{}/raw_data.json'.format(event)
        old = json.load(open(fp))
        old.append(data)
        json.dump(old, open(fp, 'w'))

    def add_match(self, event):
        if len(event) > 0 and request.is_json:
            data = request.json
            self._add_match(event, data)
            self.__update_event(event)  # TODO: Maybe don't update immediately.
            return make_response(jsonify(), 200)
        abort(400)

    def add_matches(self, event):
        if len(event) > 0 and request.is_json:
            data = request.json
            for match in data:
                self._add_match(event, match)
            self.__update_event(event)  # TODO: Maybe don't update immediately.
            return make_response(jsonify(), 200)
        abort(400)

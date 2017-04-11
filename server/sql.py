from flask import make_response, jsonify, request
from flask_sqlalchemy import SQLAlchemy

import json


class SqlServer(object):
    def __init__(self, add: classmethod, sql_db: SQLAlchemy, url_prefix=""):
        self._add = lambda *x, **y: add(*x, **y, url_prefix=url_prefix)
        self.db = sql_db
        self._register_views()

    def _register_views(self):
        self._add('/opr/events', lambda: self._get_unique_values('oprs', 'event'))
        self._add('/opr/teams', lambda: self._get_unique_values('oprs', 'team'))
        self._add('/add_entry', self.add_scouting_entry, methods=["POST"])

    def _get_unique_values(self, table, column):
        query = "SELECT DISTINCT %s FROM %s"
        data = (column, table)
        result = self.db.engine.execute(query, data)
        unique_list = list(map(lambda x: x[0], result))
        return make_response(jsonify(unique_list), 200)

    def add_scouting_entry(self):
        from server.models import ScoutingEntry
        data = request.json
        data["data"] = json.dumps(data["data"])
        try:
            entry = ScoutingEntry.query.filter_by(id=data['id']).first()
            if entry:
                entry.update(**data)
            else:
                raise KeyError('ID Not found in DB')
        except KeyError as _:
            entry = ScoutingEntry(**data)
            self.db.session.add(entry)
        self.db.session.commit()
        return make_response(jsonify({'id': entry.id}), 200)

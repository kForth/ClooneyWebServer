from flask import make_response, jsonify, request
import json


class DataServer(object):
    def __init__(self, add: classmethod, url_prefix="", working_dir=""):
        self.working_dir = working_dir
        self._add = lambda *x, **y: add(*x, **y, url_prefix=url_prefix)
        self._register_views()

    def _register_views(self):
        self._add('/headers/<event>/<key>', self.get_table_headers, methods=['GET', 'POST'])
        self._add('/headers/<event>', self.get_table_headers, methods=['GET'])

    def get_table_headers(self, event, key=None):
        file_path = self.working_dir + 'clooney/headers/{}.json'.format(event)
        headers = json.load(open(file_path))
        if request.method == "GET":
            if key is None:
                return make_response(jsonify(list(headers.keys())))
            elif key not in headers.keys():
                return make_response(jsonify("Key not found."), 400)
            else:
                for i in range(len(headers[key])):
                    headers[key][i]['sort_id'] = chr(ord('a') + i)
                return make_response(jsonify(headers[key]))
        if request.method == "POST":
            headers[key] = request.json
            json.dump(headers, open(file_path, "w+"))
            return make_response(jsonify({}))

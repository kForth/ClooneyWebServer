from flask import abort, make_response, request, jsonify


class HeadersDatabaseEndpoints:
    def __init__(self, db_interactor, add_route):
        self._db_interactor = db_interactor

        add_route('/get/header_groups/<event_key>', self.get_header_groups)
        add_route('/post/create_header_group/<event_key>', self.create_header_group, methods=('POST',))
        add_route('/post/header_group/<event_key>', self.save_header_group, methods=('POST',))
        add_route('/post/header_groups/<event_key>', self.save_header_groups, methods=('POST',))
        add_route('/remove/header_groups/<event_key>', self.save_header_groups, methods=('POST',))

    def get_header_groups(self, event_key):
        groups = self._db_interactor.get_header_groups(event_key)
        return make_response(jsonify([e.to_dict() for e in groups]), 200)

    def create_header_group(self, event_key):
        info = request.json
        group = self._db_interactor.create_header_group(event_key, request.headers['UserID'], info['path'])
        return make_response(jsonify(group.to_dict()), 200)

    def save_header_group(self, event_key):
        new_group = request.json
        self._db_interactor.set_header_group(event_key, new_group)
        return make_response("", 200)

    def save_header_groups(self, event_key):
        new_groups = request.json
        self._db_interactor.set_header_groups(event_key, new_groups)
        return make_response("", 200)

    def delete_header_group(self, event_key):
        group = request.json
        if group in self._db_interactor.get_header_groups(event_key):
            if request.headers['UserID'] == group.creator_id:
                self._db_interactor.remove_header_group(group)
                return make_response("", 200)
            return make_response("", 400)
        return abort(404)

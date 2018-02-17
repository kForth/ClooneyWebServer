from flask import abort, make_response, request, jsonify


class HeadersDatabaseEndpoints:
    def __init__(self, db_interactor, add_route):
        self._db_interactor = db_interactor

        add_route('/get/header_groups', self.get_header_groups)

        add_route('/post/create_header_group', self.create_header_group, methods=('POST',))
        add_route('/post/header_group', self.save_header_group, methods=('POST',))
        add_route('/post/header_groups', self.save_header_groups, methods=('POST',))
        add_route('/remove/header_group', self.delete_header_group, methods=('POST',))

        add_route('/get/user_event_headers/<event_key>', self.get_user_event_headers)
        add_route('/set/user_event_headers/<event_key>', self.set_user_default_header_id_for_page, methods=('POST',))
        add_route('/set/global_default_event_headers/<event_key>', self.set_default_header_id_for_page, methods=('POST',))

        add_route('/get/auto_create_event_headers/<event_key>', self.auto_create_event_headers)
        add_route('/get/auto_create_default_headers/<event_key>', self.auto_create_default_headers)

    def get_header_groups(self):
        groups = self._db_interactor.get_header_groups()
        return make_response(jsonify([e.to_dict() for e in groups]), 200)

    def create_header_group(self):
        info = request.json
        group = self._db_interactor.create_header_group(request.headers['UserID'], info['path'])
        return make_response(jsonify(group.to_dict()), 200)

    def save_header_group(self):
        new_group = request.json
        self._db_interactor.set_header_group(new_group)
        return make_response("", 200)

    def save_header_groups(self):
        new_groups = request.json
        self._db_interactor.set_header_groups(new_groups)
        return make_response("", 200)

    def delete_header_group(self):
        group = request.json
        if group in self._db_interactor.get_header_groups():
            if request.headers['UserID'] == group.creator_id:
                self._db_interactor.remove_header_group(group)
                return make_response("", 200)
            return make_response("", 400)
        return abort(404)

    def get_user_event_headers(self, event_key):
        if 'UserID' in request.headers.keys():
            user_id = request.headers['UserID']
            header_ids = self._db_interactor.get_user_event_header_ids(user_id, event_key)
        else:
            header_ids = self._db_interactor.get_default_event_header_ids(event_key)
        headers = {}
        for (path, header_id) in header_ids.items():
            headers[path] = self._db_interactor.get_header_group(header_id).to_dict()['data']
        return make_response(jsonify(headers), 200)

    def set_user_default_header_id_for_page(self, event_key):
        self._db_interactor.set_user_default_header_id_for_page(request.headers['UserID'], event_key, request.json['path'], request.json['id'])
        return make_response("", 200)

    def set_default_header_id_for_page(self, event_key):
        self._db_interactor.set_default_header_id_for_page(event_key, request.json['path'], request.json['id'])
        return make_response("", 200)

    def auto_create_event_headers(self, event_key):
        if request.json:
            pages = request.json
            headers = self._db_interactor.get_auto_generated_headers(event_key, pages)
        else:
            headers = self._db_interactor.get_auto_generated_headers(event_key)
        return make_response(headers, 200)

    def auto_create_default_headers(self, event_key):
        headers = self._db_interactor.get_auto_generated_headers(event_key)
        self._db_interactor.set_default_event_headers(headers)
        return make_response("", 200)


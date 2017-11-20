class User:
    def __init__(self, username, password, first_name, last_name, id, role="Guest"):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.id = id
        self.role = role

    def to_dict(self):
        return {
            'username':   self.username,
            'password':   self.password,
            'first_name': self.first_name,
            'last_name':  self.last_name,
            'id':         self.id,
            'role':       self.role
        }

    @staticmethod
    def verify_json(data):
        req_keys = ['username', 'password', 'first_name', 'last_name', 'id']
        opt_keys = ['role']
        return all([k in data.keys() for k in req_keys]) and all([k in opt_keys or k in req_keys for k in data.keys()])

    @staticmethod
    def from_json(data):
        return User(**data) if User.verify_json(data) else None


class ScoutingEntry:
    def __init__(self, id, event, data, filename=""):
        self.id = id
        self.event = event
        self.data = data
        self.filename = filename

    def to_dict(self):
        return {
            'id':    self.id,
            'event': self.event,
            'data':  self.data,
            'filename': self.filename
        }

    @staticmethod
    def verify_json(data):
        req_keys = ['id', 'event', 'data']
        opt_keys = ['filename']
        return all([k in data.keys() for k in req_keys]) and all([k in opt_keys or k in req_keys for k in data.keys()])

    @staticmethod
    def from_json(data):
        return ScoutingEntry(**data) if ScoutingEntry.verify_json(data) else None


class ScoutingSheetConfig:
    def __init__(self, id, name, data, date_created="", date_modified="", scan_data=[]):
        self.id = id
        self.name = name
        self.data = data
        self.date_created = date_created
        self.date_modified = date_modified
        self.scan_data = scan_data

    def to_dict(self):
        return {
            'id':    self.id,
            'name': self.name,
            'data':  self.data,
            'date_created':  self.date_created,
            'date_modified':  self.date_modified,
            'scan_data':  self.scan_data
        }

    @staticmethod
    def verify_json(data):
        req_keys = ['id', 'name', 'data']
        opt_keys = ['date_created', 'date_modified', 'scan_data']
        return all([k in data.keys() for k in req_keys]) and all([k in opt_keys or k in req_keys for k in data.keys()])

    @staticmethod
    def from_json(data):
        return ScoutingSheetConfig(**data) if ScoutingSheetConfig.verify_json(data) else None

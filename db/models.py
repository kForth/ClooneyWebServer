class User:
    def __init__(self, username, password, first_name, last_name, id, role="Guest"):
        self.username = username
        self.password_hash = password
        self.first_name = first_name
        self.last_name = last_name
        self.id = id
        self.role = role

    def to_dict(self):
        return {
            'username':   self.username,
            'password':   self.password_hash,
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

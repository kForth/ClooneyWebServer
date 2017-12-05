from flask import Flask
from flask import abort
from flask import request

from db_endpoints import *
from db_interactors import DatabaseInteractor

app = Flask(__name__)
app.config.from_pyfile('server.cfg')
db = DatabaseInteractor(app)
active_users = {}


def add_route(route, func, methods=('GET',), url_prefix="", min_role="Guest"):
    def func_with_auth(*args, **kwargs):
        user = db.users.get_user_by_id(int('0' + request.headers['UserID']))
        user_key = request.headers['UserKey']
        if min_role == "Guest" \
                or (user and db.users.USER_ROLES.index(user.role) >= db.users.USER_ROLES.index(min_role)
                    and user_key == active_users[user.username]):
            return func(*args, **kwargs)
        else:
            abort(401)

    app.add_url_rule(url_prefix + route, url_prefix + route, func_with_auth, methods=methods)

user_endpoints = UserDatabaseEndpoints(db.users, add_route, active_users)
sheet_endpoints = SheetDatabaseEndpoints(db.sheets, add_route)
event_endpoints = EventDatabaseEndpoints(db.events, add_route)
entry_endpoints = EntryDatabaseEndpoints(db.entries, add_route)
calc_endpoints = CalculatorDatabaseEndpoints(db.calculator, add_route)


@app.route('/')
def index():
    return app.send_static_file('views/index.html')

from flask import Flask, abort, request

from db_endpoints import *
from db_endpoints.headers import HeadersDatabaseEndpoints
from db_interactors import DatabaseInteractor

app = Flask(__name__)
app.config.from_pyfile('server.cfg')
db = DatabaseInteractor(app)
active_users = {}


def add_route(route, func, methods=('GET',), url_prefix="", min_role="Guest"):
    def func_with_auth(*args, **kwargs):
        if min_role == "Guest":
            return func(*args, **kwargs)
        if not all([h in request.headers for h in ['UserID', 'UserKey']]):
            abort(400)
        user_id = int(request.headers['UserID']) if request.headers['UserID'] else -1
        user = db.users.get_user_by_id(user_id)
        user_key = request.headers['UserKey']
        if user_id in active_users.keys() and user_key == active_users[user_id] and user \
                and db.users.USER_ROLES.index(user.role) >= db.users.USER_ROLES.index(min_role):
            return func(*args, **kwargs)
        else:
            abort(401)

    app.add_url_rule(url_prefix + route, url_prefix + route, func_with_auth, methods=methods)

user_endpoints = UserDatabaseEndpoints(db.users, add_route, active_users)
sheet_endpoints = SheetDatabaseEndpoints(db.sheets, add_route)
event_endpoints = EventDatabaseEndpoints(db.events, add_route)
entry_endpoints = EntryDatabaseEndpoints(db.entries, add_route)
calc_endpoints = CalculatorDatabaseEndpoints(db.calculator, add_route)
header_endpoints = HeadersDatabaseEndpoints(db.headers, add_route)


@app.route('/commit_db', methods=('POST',))
def commit():
    db.commit()
    return "", 200


@app.route('/shutdown', methods=('POST',))
def stop():
    db.commit()
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "", 200

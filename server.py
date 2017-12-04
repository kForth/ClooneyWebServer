from flask import Flask

from db_endpoints import *
from db_interactors import DatabaseInteractor

app = Flask(__name__)
app.config.from_pyfile('server.cfg')


def add_route(route, func, methods=('GET',), url_prefix=""):
    app.add_url_rule(url_prefix + route, url_prefix + route, func, methods=methods)

db = DatabaseInteractor(app)
active_users = {}
user_endpoints = UserDatabaseEndpoints(db.users, add_route, active_users)
sheet_endpoints = SheetDatabaseEndpoints(db.sheets, add_route)
event_endpoints = EventDatabaseEndpoints(db.events, add_route)
entry_endpoints = EntryDatabaseEndpoints(db.entries, add_route)
calc_endpoints = CalculatorDatabaseEndpoints(db.calculator, add_route)


@app.route('/')
def index():
    return app.send_static_file('views/index.html')

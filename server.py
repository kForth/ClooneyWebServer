from flask import Flask

from db_endpoints import EventDatabaseEndpoints, SheetDatabaseEndpoints, UserDatabaseEndpoints, EntryDatabaseEndpoints
from db_interactors import DatabaseInteractor

app = Flask(__name__)
app.config.from_pyfile('server.cfg')


def add_route(route, func, methods=('GET',), url_prefix=""):
    app.add_url_rule(url_prefix + route, url_prefix + route, func, methods=methods)

db = DatabaseInteractor(app)

user_endpoints = UserDatabaseEndpoints(db.user_interactor, add_route)
sheet_endpoints = SheetDatabaseEndpoints(db.sheet_interactor, add_route)
event_endpoints = EventDatabaseEndpoints(db.event_interactor, add_route)
entry_endpoints = EntryDatabaseEndpoints(db.entry_interactor, add_route)


# tba_endpoints = TbaDatabaseEndpoints(db.tba_interactor, app)


@app.route('/')
def index():
    return app.send_static_file('views/index.html')

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager
from flask_security import SQLAlchemyUserDatastore, Security
from tba_py import BlueAllianceAPI
import better_exceptions

from server.data import DataServer
from server.db import Database
from server.stats import StatsServer
from server.info import InfoServer
from server.receiver import ReceiverServer
from server.users import UsersServer
from server.sql import SqlServer

app = Flask(__name__, static_folder='../server/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../db/db.sqlite'  # 'postgres://localhost:5432'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "D4&u$VDtwe2Ng!q&"
sql_db = SQLAlchemy(app)


class ClooneyServer(object):
    def __init__(self):
        self.app = app
        self.sql_db = sql_db

        from server.models import OprEntry, User, Role

        self.user_datastore = SQLAlchemyUserDatastore(sql_db, User, Role)
        self.security = Security(app, self.user_datastore)

        self.sql_db.create_all()

        selfapi_manager = APIManager(app, flask_sqlalchemy_db=sql_db)
        selfapi_manager.create_api(OprEntry, methods=['GET'], results_per_page=-1, url_prefix="/api/sql/")

        self.tba = BlueAllianceAPI('kestin_goforth', 'Clooney', '1.0', enable_caching=True, cache_db_path='./tba.json')
        self.db = Database()

        self._register_views()
        self.data_server = DataServer(self._add, "/api")
        self.stats_server = StatsServer(self._add, self.db, self.sql_db, self.tba, "/api")
        self.info_server = InfoServer(self._add, self.db, self.tba, "/api")
        self.sql_server = SqlServer(self._add, self.sql_db, "/api/sql")
        self.recv_server = ReceiverServer(self._add, self.tba, self.db, url_prefix="/api/data")
        self.user_server = UsersServer(self._add, self.user_datastore, self.security)

        self.run = self.app.run

    def _register_views(self):
        self._add('/', self.index)
        self._add('/opr/', self.opr)
        self._add('/s/', self.settings)
        self._add('/a/', self.analysis)
        self._add('/account/', self.account)

    def _add(self, route: str, func: classmethod, methods=('GET',), url_prefix=""):
        self.app.add_url_rule(url_prefix + route, route, view_func=func, methods=methods)

    def index(self):
        return self.app.send_static_file('views/index.html')

    def analysis(self):
        return self.app.send_static_file('views/analysis/index.html')

    def settings(self):
        return self.app.send_static_file('views/settings/index.html')

    def account(self):
        return self.app.send_static_file('views/login.html')

    def opr(self):
        return self.app.send_static_file('views/oprs.html')


if __name__ == "__main__":
    import json
    from server.models import ScoutingEntry

    event_id = "2017onto2"
    data = json.load(open("../clooney/data/{}/raw_data.json".format(event_id)))

    for line in data:
        fields = {
            'filename': "",
            'data': json.dumps(line),
            'team': int(line["team_number"]),
            'match': int(str(line["match"]).strip("*")),
            'pos': int(line["pos"]),
            'event': event_id
        }
        entry = ScoutingEntry(**fields)
        sql_db.session.add(entry)
    sql_db.session.commit()


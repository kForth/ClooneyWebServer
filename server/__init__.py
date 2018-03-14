from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager
from tba_py import TBA
import better_exceptions

from server.data import DataServer
from server.db import Database
from server.stats import StatsServer
from server.info import InfoServer
from server.users import UsersServer
from server.sql import SqlServer

app = Flask(__name__, static_folder='../server/static')
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../db/db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "D4&u$VDtwe2Ng!q&"
sql_db = SQLAlchemy(app)


class ClooneyServer(object):
    def __init__(self):
        self.app = app
        self.sql_db = sql_db

        from server.models import OprEntry, User

        self.sql_db.create_all()

        self.api_manager = APIManager(app, flask_sqlalchemy_db=sql_db)
        self.api_manager.create_api(OprEntry, methods=['GET'], results_per_page=-1, url_prefix="/api/sql/")

        root_path = '/'.join(app.root_path.split('/')[:-1]) + '/'
        self.tba = TBA('GdZrQUIjmwMZ3XVS622b6aVCh8CLbowJkCs5BmjJl2vxNuWivLz3Sf3PaqULUiZW', use_cache=False, cache_filename=root_path + 'tba.json')
        self.db = Database(path_prefix=root_path)

        self._register_views()
        self.data_server = DataServer(self._add, "/api", working_dir=root_path)
        self.stats_server = StatsServer(self._add, self.db, self.sql_db, self.tba, "/api", root_path)
        self.info_server = InfoServer(self._add, self.db, self.sql_db, self.tba, "/api", path_prefix=root_path)
        self.sql_server = SqlServer(self._add, self.sql_db, "/api/sql")
        self.user_server = UsersServer(self._add, url_prefix="/user")

        self.run = self.app.run

    def _register_views(self):
        self._add('/', self.index)
        self._add('/printable_stats', self.printable_stats)

    def _add(self, route: str, func: classmethod, methods=('GET',), url_prefix=""):
        self.app.add_url_rule(url_prefix + route, url_prefix + route, view_func=func, methods=methods)

    def printable_stats(self):
        return self.app.send_static_file('views/printable_stats.html')

    def index(self):
        return self.app.send_static_file('views/index.html')


server = ClooneyServer()

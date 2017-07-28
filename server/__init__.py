import better_exceptions
from flask import Flask

app = Flask(__name__, static_folder='../static')
app.config.from_pyfile('../server.cfg')

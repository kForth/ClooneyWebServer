from flask import Flask

from tba import TBA

app = Flask(__name__, static_folder='../static')
app.config.from_pyfile('../server.cfg')
tba = TBA('KestinGoforth', 'Clooney', '3')

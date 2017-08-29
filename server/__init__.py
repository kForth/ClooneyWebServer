from flask import Flask

from tba import TBA

app = Flask(__name__, static_folder='../static')
app.config.from_pyfile('../server.cfg')
tba = TBA(app.config['TBA_AUTH_KEY'])


@app.route('/')
def index():
    return app.send_static_file('views/index.html')

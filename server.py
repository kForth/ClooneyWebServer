from flask import Flask

from tba import TBA

from db import DatabaseInteractor

app = Flask(__name__)
app.config.from_pyfile('server.cfg')
tba = TBA(app.config['TBA_AUTH_KEY'])
db = DatabaseInteractor(app.root_path)


@app.route('/')
def index():
    return app.send_static_file('views/index.html')


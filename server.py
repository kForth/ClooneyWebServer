from flask import Flask

from db import DatabaseInteractor

app = Flask(__name__)
app.config.from_pyfile('server.cfg')
db = DatabaseInteractor(app)


@app.route('/')
def index():
    return app.send_static_file('views/index.html')


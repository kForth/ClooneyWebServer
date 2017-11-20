from flask import Flask

from db import DatabaseInteractor

app = Flask(__name__)
app.config.from_pyfile('server.cfg')
app.add_route = lambda route, func, methods=('GET',), url_prefix="": app.add_url_rule(url_prefix + route,
                                                                                      url_prefix + route, func,
                                                                                      methods=methods)
db = DatabaseInteractor(app)


@app.route('/')
def index():
    return app.send_static_file('views/index.html')

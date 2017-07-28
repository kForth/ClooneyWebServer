from flask_sqlalchemy import SQLAlchemy

from server import app

sql_db = SQLAlchemy(app)

if __name__ == "__main__":
    # from server.db import sql_db
    from server.db.models import *
    sql_db.create_all()

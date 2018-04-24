"""Module that exposes database connections"""

from flask_sqlalchemy import SQLAlchemy


# pylint: disable=C0103,E1101
db = SQLAlchemy()
joinedload = db.joinedload

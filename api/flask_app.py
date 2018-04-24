"""Flask main app instance creator"""

import os
from flask import Flask
from models.storage import db


# pylint: disable=C0103
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

try:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['MINTAX_DB_URL']
    app.config['SQLALCHEMY_ECHO'] = False
except KeyError:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://jack:@localhost/mintax'
    app.config['SQLALCHEMY_ECHO'] = True

try:
    app.config['REDIS_URL'] = os.environ['REDIS_URL']
except KeyError:
    app.config['REDIS_URL'] = 'redis://localhost'

db.init_app(app)

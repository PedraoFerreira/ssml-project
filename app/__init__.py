from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

__author__ = 'ssml'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

from app.controllers import default
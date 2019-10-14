from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import os

__author__ = 'ssml'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config.from_object(os.environ.get('SSML_CONFIG_CLASS', 'config.Production'))
db = SQLAlchemy(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

from app.controllers import default
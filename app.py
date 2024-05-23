from os import getenv

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_migrate import Migrate

from blueprints.templates import Template, templates_blueprint
from models import db

load_dotenv()

application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URI')

application.register_blueprint(
    templates_blueprint,
    url_prefix='/templates',
)

db.init_app(application)
migrate = Migrate(application, db)

@application.get('/')
def index():
    return render_template('base.html')

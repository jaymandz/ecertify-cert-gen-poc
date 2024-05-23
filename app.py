from os import getenv

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from dotenv import load_dotenv

from blueprints.templates import templates_blueprint

load_dotenv()

application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URI')

application.register_blueprint(
    templates_blueprint,
    url_prefix='/templates',
)

db = SQLAlchemy(application)
migrate = Migrate(application, db)

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    content = db.Column(db.Text())

@application.get('/')
def index():
    return render_template('base.html')

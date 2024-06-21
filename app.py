from os import getenv

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_migrate import Migrate

from blueprints.api import api_blueprint
from blueprints.certificate_types import certificate_types_blueprint
from blueprints.certificates import certificates_blueprint
from blueprints.templates import templates_blueprint
from models import db

load_dotenv()

application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URI')

application.register_blueprint(
    api_blueprint,
    url_prefix='/api',
)
application.register_blueprint(
    certificate_types_blueprint,
    url_prefix='/certificate-types',
)
application.register_blueprint(
    certificates_blueprint,
    url_prefix='/certificates',
)
application.register_blueprint(
    templates_blueprint,
    url_prefix='/templates',
)

db.init_app(application)
migrate = Migrate(application, db)

@application.get('/')
def index():
    return render_template('index.html')

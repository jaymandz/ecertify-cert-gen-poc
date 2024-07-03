from flask import Blueprint

from blueprints.api.certificate_types import certificate_types_blueprint
from blueprints.api.certificates import certificates_blueprint
from blueprints.api.templates import templates_blueprint

api_blueprint = Blueprint('api', __name__)

api_blueprint.register_blueprint(
    certificate_types_blueprint,
    url_prefix='/certificate-types',
)
api_blueprint.register_blueprint(
    certificates_blueprint,
    url_prefix='/certificates',
)
api_blueprint.register_blueprint(
    templates_blueprint,
    url_prefix='/templates',
)
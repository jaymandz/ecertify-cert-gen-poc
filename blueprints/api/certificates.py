from flask import Blueprint

from blueprints.api.recipients import (
    dict_from_scalar as recipient_dict_from_scalar
)
from models import Certificate, db

certificates_blueprint = Blueprint('certificates', __name__)

@certificates_blueprint.get('/<int:id>')
def show(id):
    c = db.get_or_404(Certificate, id)
    return {
        'id': c.id,
        'name': c.name,
        'recipients': [ recipient_dict_from_scalar(r) for r in c.recipients ],
    }
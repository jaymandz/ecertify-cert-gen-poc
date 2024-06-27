from flask import Blueprint, request

from models import Certificate, db

recipients_blueprint = Blueprint('recipients', __name__)

@recipients_blueprint.get('/create')
def create():
    c = db.get_or_404(Certificate, request.args.get('certificate_id'))
    return 'Under construction'
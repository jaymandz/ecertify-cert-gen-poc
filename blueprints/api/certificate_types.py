from flask import Blueprint

from models import CertificateType, db

certificate_types_blueprint = Blueprint('certificate_types', __name__)

def dict_from_scalar(t): return {
    'id': t.id,
    'name': t.name,
    'fields': [
        {
            'id': f.id,
            'description': f.description,
            'value_type': f.value_type.value,
            'is_required': f.is_required,
        }
        for f in t.fields
    ],
}

@certificate_types_blueprint.get('/')
def index():
    return [
        dict_from_scalar(t)
        for t in db.session.execute(db.select(CertificateType)).scalars()
    ]

@certificate_types_blueprint.get('/<int:id>')
def show(id):
    return dict_from_scalar(db.get_or_404(CertificateType, id))
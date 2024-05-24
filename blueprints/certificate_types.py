from flask import Blueprint, redirect, render_template, request, url_for

from models import CertificateType, CertificateTypeField, db

certificate_types_blueprint = Blueprint('certificate_types', __name__)

@certificate_types_blueprint.get('/')
def index():
    return render_template(
        'certificate-types/index.html',
        title='Certificate types',
        collection=db.paginate(db.select(CertificateType))
    )

@certificate_types_blueprint.get('/create')
def create():
    return render_template(
        'certificate-types/create.html',
        title='Create a certificate type',
    )

@certificate_types_blueprint.get('/<int:id>')
def show(id):
    t = db.get_or_404(CertificateType, id)
    return 'Under construction'
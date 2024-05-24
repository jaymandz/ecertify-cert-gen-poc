from flask import Blueprint, render_template

from models import CertificateType, CertificateTypeField, db

certificate_types_blueprint = Blueprint('certificate_types', __name__)

@certificate_types_blueprint.get('/')
def index():
    return render_template(
        'certificate-types/index.html',
        title='Certificate types',
    )

@certificate_types_blueprint.get('/create')
def create():
    return render_template(
        'certificate-types/create.html',
        title='Create a certificate type',
    )
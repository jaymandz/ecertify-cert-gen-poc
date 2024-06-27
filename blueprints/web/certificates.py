import re

from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy import func

from models import (
    Certificate,
    CertificateField,
    CertificateType,
    CertificateTypeField,
    Template,
    db,
)

certificates_blueprint = Blueprint('certificates', __name__)

@certificates_blueprint.get('/')
def index():
    collection = db.select(Certificate).where(
        Certificate.name.ilike(f'%{request.args.get('q', '')}%')
    )

    return render_template(
        'certificates/index.html',
        title='Certificates',
        table_count=db.session.query(func.count(Certificate.id)).scalar(),
        collection=db.paginate(collection),
    )

@certificates_blueprint.get('/create')
def create():
    return render_template(
        'certificates/create.html',
        title='Create a certificate',
        certificate_types=db.session.execute(
            db.select(CertificateType)
        ).scalars(),
    )

@certificates_blueprint.post('/')
def store():
    c = Certificate()
    c.template_id = int(request.form['template_id'])
    c.name = request.form['name']
    c.issuance_date = request.form['issuance_date']
    c.issuance_locale = request.form['issuance_locale']

    db.session.add(c)

    for field_name in request.form:
        if not re.match('field__', field_name): continue

        ctype_id = db.session.execute(
            db.select(Template).where(Template.id==c.template_id)
        ).scalar_one().certificate_type_id

        tf = db.session.execute(
            db.select(CertificateTypeField). \
              where(CertificateTypeField.certificate_type_id == ctype_id). \
              where(CertificateTypeField.name == field_name[7:])
        ).scalar_one()

        cf = CertificateField()
        cf.certificate_id = c.id
        cf.certificate_type_field_id = tf.id
        cf.value = request.form[field_name]
        db.session.add(cf)

    db.session.commit()
    return redirect(url_for('certificates.index'))

@certificates_blueprint.get('/<int:id>')
def show(id):
    c = db.get_or_404(Certificate, id)
    return render_template(
        'certificates/show.html',
        title=f'Certificate "{c.name}"',
        certificate=c,
    )

@certificates_blueprint.get('/<int:id>/edit')
def edit(id):
    c = db.get_or_404(Certificate, id)
    return 'Under construction'
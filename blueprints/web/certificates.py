import re

from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy import and_, func, or_

from models import (
    Certificate,
    CertificateField,
    CertificateType,
    CertificateTypeField,
    Recipient,
    Template,
    db,
)

certificates_blueprint = Blueprint('certificates', __name__)

def insert_fields(certificate):
    ctype_id = db.session.execute(
        db.select(Template).where(Template.id == certificate.template_id)
    ).scalar_one().certificate_type_id

    for field_name in request.form:
        if not re.match('field__', field_name): continue

        tf = db.session.execute(db.select(CertificateTypeField).where(and_(
            CertificateTypeField.certificate_type_id == ctype_id,
            CertificateTypeField.name == field_name[7:],
        ))).scalar_one()

        cf = CertificateField()
        cf.certificate_id = certificate.id
        cf.certificate_type_field_id = tf.id
        cf.value = request.form[field_name]
        db.session.add(cf)

def update_fields(certificate):
    for field_name in request.form:
        if not re.match('field__', field_name): continue

        cf = db.session.execute(db.select(CertificateField).where(and_(
            CertificateField.certificate_id == certificate.id,
            CertificateField.certificate_type_field.name == field_name[7:],
        )))
        cf.value = request.form[field_name]

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
        'certificates/create-edit.html',
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

    insert_fields(c)

    db.session.commit()
    return redirect(url_for('certificates.index'))

@certificates_blueprint.get('/<int:id>')
def show(id):
    c = db.get_or_404(Certificate, id)

    collection = db.select(Recipient). \
        where(Recipient.certificate_id==c.id).where(or_(
            Recipient.last_name.ilike(f'%{request.args.get('q', '')}%'),
            Recipient.first_name.ilike(f'%{request.args.get('q', '')}%'),
            Recipient.middle_name.ilike(f'%{request.args.get('q', '')}%'),
            Recipient.honorific.ilike(f'%{request.args.get('q', '')}%'),
            Recipient.suffix.ilike(f'%{request.args.get('q', '')}%'),
            Recipient.organization.ilike(f'%{request.args.get('q', '')}%'),
            Recipient.address.ilike(f'%{request.args.get('q', '')}%'),
        ))

    return render_template(
        'certificates/show.html',
        title=f'Certificate "{c.name}"',
        certificate=c,
        collection=db.paginate(collection),
    )

@certificates_blueprint.get('/<int:id>/edit')
def edit(id):
    c = db.get_or_404(Certificate, id)
    return render_template(
        'certificates/create-edit.html',
        title=f'Edit certificate "{c.name}"',
        certificate=c,
        certificate_types=db.session.execute(
            db.select(CertificateType)
        ).scalars(),
    )

@certificates_blueprint.post('/<int:id>')
def update(id):
    c = db.get_or_404(Certificate, id)

    c.template_id = request.form['template_id']
    c.name = request.form['name']
    c.issuance_date = request.form['issuance_date']
    c.issuance_locale = request.form['issuance_locale']

    t = db.session.execute(
        db.select(Template).where(Template.id == c.template_id)
    ).scalar_one()
    if t.certificate_type_id == request.form['template_id']:
        update_fields(c)
    else:
        db.session.execute(db.delete(CertificateField).where(
            CertificateField.certificate_id == c.id
        ))
        insert_fields(c)

    db.session.commit()
    return redirect(url_for('certificates.show', id=c.id))

@certificates_blueprint.post('/<int:id>/delete')
def delete(id):
    return 'Under construction'

@certificates_blueprint.post('/<int:id>/zip')
def zip(id):
    return 'Under construction'
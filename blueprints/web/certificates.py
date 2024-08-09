import csv
import io
import re

import random
import string

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
        if not re.match('field__', field_name):
            continue

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
        if not re.match('field__', field_name):
            continue

        cf = db.session.execute(db.select(CertificateField).where(and_(
            CertificateField.certificate_id == certificate.id,
            CertificateField.certificate_type_field.name == field_name[7:],
        )))
        cf.value = request.form[field_name]

def generate_token():
    # TODO: DRY this function
    while True:
        token = ''.join(random.choice(string.ascii_letters) for _ in range(13))
        query = db.select(Recipient).where(Recipient.token==token)
        if not db.session.execute(query).scalar_one_or_none():
            break

    return token

def get_recipient_by_token(token):
    return db.session.execute(
        db.select(Recipient).where(Recipient.token == token)
    ).scalar_one()

def delete_recipient_by_token(token):
    db.session.delete(get_recipient_by_token(token))

@certificates_blueprint.get('/')
def index():
    collection = db.select(Certificate).where(
        Certificate.name.ilike(f'%{request.args.get("q", "")}%')
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
    ec = db.session.execute(
        db.select(Certificate).where(Certificate.name==request.form['name'])
    ).scalar_one_or_none()
    if ec:
        return redirect(url_for(
            'certificates.create',
            messages=['name-taken'],
        ))

    c = Certificate()
    c.template_id = int(request.form['template_id'])
    c.name = request.form['name']
    c.issuance_date = request.form['issuance_date']
    c.issuance_locale = request.form['issuance_locale']

    db.session.add(c)

    insert_fields(c)

    db.session.commit()
    return redirect(url_for(
        'certificates.index',
        messages=['store-success'],
    ))

@certificates_blueprint.get('/<int:id>')
def show(id):
    c = db.get_or_404(Certificate, id)

    collection = db.select(Recipient). \
        where(Recipient.certificate_id==c.id).where(or_(
            Recipient.last_name.ilike(f'%{request.args.get("q", "")}%'),
            Recipient.first_name.ilike(f'%{request.args.get("q", "")}%'),
            Recipient.middle_name.ilike(f'%{request.args.get("q", "")}%'),
            Recipient.honorific.ilike(f'%{request.args.get("q", "")}%'),
            Recipient.suffix.ilike(f'%{request.args.get("q", "")}%'),
            Recipient.organization.ilike(f'%{request.args.get("q", "")}%'),
            Recipient.address.ilike(f'%{request.args.get("q", "")}%'),
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
    ec = db.session.execute(db.select(Certificate).where(and_(
        Certificate.id!=id,
        Certificate.name==request.form['name']),
    )).scalar_one_or_none()
    if ec:
        return redirect(url_for(
            'certificates.edit',
            id=id,
            messages=['name-taken'],
        ))

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
    return redirect(url_for(
        'certificates.show',
        id=c.id,
        messages=['update-success'],
    ))

@certificates_blueprint.post('/<int:id>/delete')
def delete(id):
    c = db.get_or_404(Certificate, id)

    # Delete the certificate fields first
    db.session.execute(db.delete(CertificateField).where(
        CertificateField.certificate_id==c.id
    ))
    # Then the recipients
    db.session.execute(db.delete(Recipient).where(
        Recipient.certificate_id==c.id
    ))
    # And finally the certificate itself
    db.session.delete(c)

    db.session.commit()
    return redirect(url_for(
        'certificates.index',
        messages=['delete-success'],
    ))

@certificates_blueprint.get('/<int:id>/csv')
def recipients_csv_upload(id):
    c = db.get_or_404(Certificate, id)
    return render_template(
        'certificates/recipients-csv.html',
        title=f'Add recipients for certificate "{c.name}" through CSV',
        certificate=c,
    )

@certificates_blueprint.post('/<int:id>/csv')
def recipients_csv_store(id):
    c = db.get_or_404(Certificate, id)

    if request.files['file']:
        stream = request.files['file'].stream
        contents = stream.read().decode('utf-8')
    else:
        contents = request.form['text']

    for row in csv.reader(io.StringIO(contents)):
        r = Recipient()

        r.token = generate_token()
        r.certificate_id = c.id
        r.last_name = row[0]
        r.first_name = row[1]

        try:
            r.middle_name = row[2]
        except IndexError:
            r.middle_name = ''

        try:
            r.honorific = row[3]
        except IndexError:
            r.honorific = ''

        try:
            r.suffix = row[4]
        except IndexError:
            r.suffix = ''

        try:
            r.organization = row[5]
        except IndexError:
            r.organization = ''

        try:
            r.address = row[6]
        except IndexError:
            r.address = ''

        db.session.add(r)

    db.session.commit()

    return redirect(url_for(
        'certificates.show',
        id=c.id,
        messages=['csv-store-success'],
    ))

@certificates_blueprint.get('/<int:id>/batch')
def recipients_batch_edit(id):
    c = db.get_or_404(Certificate, id)
    return render_template(
        'certificates/recipients-batch.html',
        title=f'Edit recipients of certificate "{c.name}" as a batch',
        certificate=c,
    )

@certificates_blueprint.post('/<int:id>/batch')
def recipients_batch_update(id):
    c = db.get_or_404(Certificate, id)

    recipient_tokens = request.form.getlist('recipient-tokens')
    recipient_statuses = request.form.getlist('recipient-statuses')
    recipient_last_names = request.form.getlist('recipient-last-names')
    recipient_first_names = request.form.getlist('recipient-first-names')
    recipient_middle_names = request.form.getlist('recipient-middle-names')
    recipient_honorifics = request.form.getlist('recipient-honorifics')
    recipient_suffixes = request.form.getlist('recipient-suffixes')
    recipient_organizations = request.form.getlist('recipient-organizations')
    recipient_addresses = request.form.getlist('recipient-addresses')

    def assign_values_to_recipient(recipient, i):
        recipient.last_name = recipient_last_names[i]
        recipient.first_name = recipient_first_names[i]
        recipient.middle_name = recipient_middle_names[i]
        recipient.honorific = recipient_honorifics[i]
        recipient.suffix = recipient_suffixes[i]
        recipient.organization = recipient_organizations[i]
        recipient.address = recipient_addresses[i]

    for i, status in enumerate(recipient_statuses):
        if status == 'to-add':
            recipient = Recipient()
            recipient.token = generate_token()
            recipient.certificate_id = c.id
            assign_values_to_recipient(recipient, i)
            db.session.add(recipient)
        elif status == 'to-edit':
            recipient = get_recipient_by_token(recipient_tokens[i])
            assign_values_to_recipient(recipient, i)
        elif status == 'to-delete':
            delete_recipient_by_token(recipient_tokens[i])

    db.session.commit()

    return redirect(url_for(
        'certificates.show',
        id=c.id,
        messages=['recipient-batch-manage-success'],
    ))
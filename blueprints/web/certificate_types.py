from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy import and_, func

from models import CertificateType, CertificateTypeField, db

certificate_types_blueprint = Blueprint('certificate_types', __name__)

def save_fields(t):
    field_ids = [ int(id) for id in request.form.getlist('field-ids') ]
    field_names = request.form.getlist('field-names')
    field_descriptions = request.form.getlist('field-descriptions')
    field_value_types = request.form.getlist('field-value-types')
    field_required_flags = request.form.getlist('field-required-flags')
    field_statuses = request.form.getlist('field-statuses')

    for index, id in enumerate(field_ids):
        if field_statuses[index] == 'to-add':
            f = CertificateTypeField()
            f.certificate_type_id = t.id
            f.name = field_names[index]
            f.description = field_descriptions[index]
            f.value_type = field_value_types[index]

            try: f.is_required = field_required_flags[index] == 'true'
            except IndexError: f.is_required = False

            db.session.add(f)
        elif field_statuses[index] == 'to-edit':
            f = db.get_or_404(CertificateTypeField, id)
            f.certificate_type_id = t.id
            f.name = field_names[index]
            f.description = field_descriptions[index]
            f.value_type = field_value_types[index]

            try: f.is_required = field_required_flags[index] == 'true'
            except IndexError: f.is_required = False
        elif field_statuses[index] == 'to-delete':
            db.session.delete(db.get_or_404(CertificateTypeField, id))

@certificate_types_blueprint.get('/')
def index():
    collection = db.select(CertificateType).where(
        CertificateType.name.ilike(f'%{request.args.get("q", "")}%')
    )

    return render_template(
        'certificate-types/index.html',
        title='Certificate types',
        table_count=db.session.query(func.count(CertificateType.id)).scalar(),
        collection=db.paginate(collection),
    )

@certificate_types_blueprint.get('/create')
def create():
    return render_template(
        'certificate-types/create-edit.html',
        title='Create a certificate type',
    )

@certificate_types_blueprint.post('/')
def store():
    et = db.session.execute(db.select(CertificateType).where(
        CertificateType.name==request.form['name']
    )).scalar_one_or_none()
    if et: return redirect(url_for(
        'certificate_types.create',
        errors=['name-taken'],
    ))

    t = CertificateType()
    t.name = request.form['name']

    db.session.add(t)
    db.session.commit()

    save_fields(t)
    
    db.session.commit()
    return redirect(url_for('certificate_types.index'))

@certificate_types_blueprint.get('/<int:id>')
def show(id):
    t = db.get_or_404(CertificateType, id)
    return render_template(
        'certificate-types/show.html',
        title=f'Certificate type "{t.name}"',
        certificate_type=t,
    )

@certificate_types_blueprint.get('/<int:id>/edit')
def edit(id):
    t = db.get_or_404(CertificateType, id)
    return render_template(
        'certificate-types/create-edit.html',
        title=f'Edit certificate type "{t.name}"',
        certificate_type=t,
    )

@certificate_types_blueprint.post('/<int:id>')
def update(id):
    et = db.session.execute(db.select(CertificateType).where(and_(
        CertificateType.id!=id,
        CertificateType.name==request.form['name'],
    ))).scalar_one_or_none()
    if et: return redirect(url_for(
        'certificate_types.edit',
        id=id,
        errors=['name-taken'],
    ))

    t = db.get_or_404(CertificateType, id)
    t.name = request.form['name']

    save_fields(t)

    db.session.commit()
    return redirect(url_for('certificate_types.show', id=id))

@certificate_types_blueprint.post('/<int:id>/delete')
def delete(id):
    db.session.delete(db.get_or_404(CertificateType, id))
    db.session.commit()
    return redirect(url_for('certificate_types.index'))

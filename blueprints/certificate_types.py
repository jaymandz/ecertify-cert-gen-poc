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

@certificate_types_blueprint.post('/')
def store():
    t = CertificateType()
    t.name = request.form['name']

    db.session.add(t)

    field_ids = [ int(id) for id in request.form.getlist('field-ids') ]
    field_descriptions = request.form.getlist('field-descriptions')
    field_value_types = request.form.getlist('field-value-types')
    field_required_flags = request.form.getlist('field-required-flags')

    for index, id in enumerate(field_ids):
        if id == 0:
            f = CertificateTypeField()
            f.description = field_descriptions[index]
            f.value_type = field_value_types[index]

            try: f.is_required = field_required_flags[0] == true
            except IndexError: f.is_required = False

            db.session.add(f)
        else:
            f = db.get_or_404(CertificateTypeField, id)
            f.description = field_descriptions[index]
            f.value_type = field_value_types[index]

            try: f.is_required = field_required_flags[0] == true
            except IndexError: f.is_required = False
    
    db.session.commit()
    return redirect(url_for('certificate_types.index'))

@certificate_types_blueprint.get('/<int:id>')
def show(id):
    t = db.get_or_404(CertificateType, id)
    return 'Under construction'
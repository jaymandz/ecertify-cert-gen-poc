from flask import Blueprint, render_template, request
from sqlalchemy import func

from models import Certificate, CertificateType, db

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
    return request.form
    c = Certificate()
    c.name = request.form['name']
    c.issuance_date = request.form['issuance_date']
    c.issuance_locale = request.form['issuance_locale']

    db.session.add(c)
    db.session.commit()
    return redirect(url_for('certificates.index'))
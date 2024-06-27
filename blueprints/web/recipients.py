from flask import Blueprint, redirect, render_template, request, url_for

from models import Certificate, Recipient, db

recipients_blueprint = Blueprint('recipients', __name__)

@recipients_blueprint.get('/create')
def create():
    c = db.get_or_404(Certificate, request.args.get('certificate_id'))
    return render_template(
        'recipients/create.html',
        title='Create a recipient',
        certificate=c,
    )

@recipients_blueprint.post('/')
def store():
    r = Recipient()
    r.certificate_id = int(request.form['certificate_id'])
    r.last_name = request.form['last_name']
    r.first_name = request.form['first_name']
    r.middle_name = request.form['middle_name']
    r.honorific = request.form['honorific']
    r.suffix = request.form['suffix']
    r.organization = request.form['organization']
    r.address = request.form['address']

    db.session.add(r)
    db.session.commit()

    return redirect(
        url_for('certificates.show', id=request.form['certificate_id'])
    )

@recipients_blueprint.get('/<int:id>')
def show(id):
    return 'Under construction'
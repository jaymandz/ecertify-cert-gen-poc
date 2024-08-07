from flask import Blueprint, redirect, render_template, request, url_for

from models import CertificateType, Template, db

templates_blueprint = Blueprint('templates', __name__)

@templates_blueprint.get('/create')
def create():
    t = db.get_or_404(CertificateType, request.args.get('certificate_type_id'))
    return render_template(
        'templates/create-edit.html',
        title='Create a template',
        certificate_type=t,
    )

@templates_blueprint.post('/')
def store():
    t = Template()
    t.certificate_type_id = int(request.form['certificate_type_id'])
    t.name = request.form['name']
    t.content = request.form['content']

    db.session.add(t)
    db.session.commit()

    return redirect(url_for('certificate_types.show', id=t.certificate_type_id))

@templates_blueprint.get('/<int:id>')
def show(id):
    t = db.get_or_404(Template, id)
    return render_template(
        'templates/show.html',
        title=f'Template "{t.name}"',
        template=t,
    )

@templates_blueprint.get('/<int:id>/edit')
def edit(id):
    t = db.get_or_404(Template, id)
    return render_template(
        'templates/create-edit.html',
        title=f'Edit template "{t.name}"',
        template=t,
    )

@templates_blueprint.post('/<int:id>')
def update(id):
    t = db.get_or_404(Template, id)
    t.name = request.form['name']
    t.content = request.form['content']

    db.session.commit()

    return redirect(url_for('templates.show', id=id))

@templates_blueprint.post('/<int:id>/delete')
def delete(id):
    t = db.get_or_404(Template, id)
    db.session.delete(t)
    db.session.commit()
    return redirect(
        url_for('certificate_types.show', id=t.certificate_type_id)
    )

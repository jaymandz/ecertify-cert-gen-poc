from flask import Blueprint, redirect, render_template, request, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

from models import Template, db

templates_blueprint = Blueprint('templates', __name__)

@templates_blueprint.get('/')
def index():
    return render_template(
        'templates/index.html',
        title='Templates',
        collection=db.paginate(db.select(Template)),
    )

@templates_blueprint.get('/create')
def create():
    return render_template(
        'templates/create.html',
        title='Create a template',
    )

@templates_blueprint.post('/')
def store():
    t = Template()
    t.name = request.form['name']
    t.content = request.form['content']

    db.session.add(t)
    db.session.commit()

    return redirect(url_for('templates.index'))

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
        'templates/edit.html',
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

@templates_blueprint.delete('/<int:id>')
def delete(id):
    return {}

from flask import Blueprint, render_template

templates_blueprint = Blueprint('templates', __name__)

@templates_blueprint.get('/')
def index():
    return render_template(
        'templates/index.html',
        title='Templates',
        collection=[],
    )

@templates_blueprint.get('/create')
def create():
    return render_template(
        'templates/create.html',
        title='Create a template',
    )

@templates_blueprint.post('/')
def store():
    return {}

@templates_blueprint.get('/<id>')
def show(id):
    return {}

@templates_blueprint.get('/<id>/edit')
def edit(id):
    return {}

@templates_blueprint.patch('/<id>')
def update(id):
    return {}

@templates_blueprint.delete('/<id>')
def delete(id):
    return {}

from flask import Blueprint

from models import Template, db

templates_blueprint = Blueprint('templates', __name__)

def dict_from_scalar(t): return {
    'id': t.id,
    'certificate_type_id': t.certificate_type_id,
    'name': t.name,
    'content': t.content,
}

@templates_blueprint.get('/')
def index():
    return [
        dict_from_scalar(t)
        for t in db.session.execute(db.select(Template)).scalars()
    ]

@templates_blueprint.get('/<int:id>')
def show(id):
    return dict_from_scalar(db.get_or_404(Template, id))
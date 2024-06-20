from flask import Blueprint, render_template

certificates_blueprint = Blueprint('certificates', __name__)

@certificates_blueprint.get('/')
def index():
    return render_template(
        'certificates/index.html',
        title='Certificates',
    )

@certificates_blueprint.get('/create')
def create():
    return render_template(
        'certificates/create.html',
        title='Create a certificate',
    )
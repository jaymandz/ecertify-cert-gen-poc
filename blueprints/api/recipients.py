from flask import Blueprint

recipients_blueprint = Blueprint('recipients', __name__)

def dict_from_scalar(s): return {
    'token': s.token,
    'last_name': s.last_name,
    'first_name': s.first_name,
    'middle_name': s.middle_name,
    'honorific': s.honorific,
    'suffix': s.suffix,
    'organization': s.organization,
    'address': s.address,
}

@recipients_blueprint.post('/')
def store():
    return 'Under construction'
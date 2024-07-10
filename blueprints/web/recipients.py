import base64
import io
import os
import random
import string

from datetime import datetime
from xml.dom.minidom import Text, parse

import qrcode
from cairosvg import svg2pdf
from dotenv import load_dotenv
from flask import (
    Blueprint, Response, redirect, render_template, request, url_for
)

from models import Certificate, Recipient, db

load_dotenv(f'{os.path.dirname(__file__)}/.env')

recipients_blueprint = Blueprint('recipients', __name__)

def complete_name(recipient):
    cn = recipient.last_name
    if recipient.middle_name:
        cn = f'{recipient.middle_name} {cn}'
    cn = f'{recipient.first_name} {cn}'
    if recipient.honorific:
        cn = f'{recipient.honorific} {cn}'
    if recipient.suffix:
        cn += f', {recipient.suffix}'
    return cn

def recipient_copy_svg_bytestr(recipient):
    template = recipient.certificate.template

    overview_url = os.getenv('ECPOC_BASE_URL')
    overview_url += url_for('recipients.overview', token=recipient.token)

    qr_stream = io.BytesIO()
    qrcode.make(overview_url).save(qr_stream)
    qr_stream.seek(0)
    qr_str = base64.b64encode(qr_stream.read()).decode('ascii')

    svg_tree = parse(io.StringIO(template.content))

    for t in svg_tree.getElementsByTagName('tspan'):
        if not t.firstChild:
            continue
        if type(t.firstChild) is not Text:
            continue

        text = t.firstChild.data

        text = text.replace('[ISSUANCE_DATE]',
          issuance_date_strftime(recipient.certificate.issuance_date))
        text = text.replace('[ISSUANCE_LOCALE]',
          recipient.certificate.issuance_locale)
        
        text = text.replace('[RECIPIENT:COMPLETE_NAME]',
          complete_name(recipient))
        text = text.replace('[R:CN]', complete_name(recipient))

        for field in recipient.certificate.fields:
            name = field.certificate_type_field.name
            value = field.value \
              if field.certificate_type_field.value_type.value == 'text' else \
              date_strftime(field.value)

            text = text.replace(f'[FIELD:{name}]', value)
            text = text.replace(f'[F:{name}]', value)

        t.firstChild.data = text
    
    for t in svg_tree.getElementsByTagName('image'):
        if t.getAttribute('id') == 'QR_CODE':
            t.setAttribute('xlink:href', f'data:image/png;base64,{qr_str}')
            break

    return svg_tree.toxml(encoding='UTF-8')

def date_strftime(dv):
    date_format = '%B '+str(dv.day)+', %Y'
    return datetime.strptime(dv, '%Y-%m-%d').strftime(date_format)

def generate_token():
    while True:
        token = ''.join(random.choice(string.ascii_letters) for _ in range(13))
        query = db.select(Recipient).where(Recipient.token==token)
        if not db.session.execute(query).scalar_one_or_none():
            break

    return token

def issuance_date_strftime(d):
    ordinal = str(d.day)
    if d.day != 11 and d.day % 10 == 1:
        ordinal += 'st'
    elif d.day != 12 and d.day % 10 == 2:
        ordinal += 'nd'
    elif d.day != 13 and d.day % 10 == 3:
        ordinal += 'rd'
    else:
        ordinal += 'th'

    date_format = ordinal+' day of %B %Y'
    return d.strftime(date_format)

@recipients_blueprint.get('/create')
def create():
    c = db.get_or_404(Certificate, request.args.get('certificate_id'))
    return render_template(
        'recipients/create-edit.html',
        title='Create a recipient',
        certificate=c,
    )

@recipients_blueprint.post('/')
def store():
    r = Recipient()
    r.token = generate_token()
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

@recipients_blueprint.get('/<token>')
def show(token):
    r = db.get_or_404(Recipient, token)
    return render_template(
        'recipients/show.html',
        title=f'{r.last_name}, {r.first_name} ({r.token})',
        recipient=r,
        svg_text=recipient_copy_svg_bytestr(r).decode('UTF-8'),
    )

@recipients_blueprint.get('/<token>/edit')
def edit(token):
    r = db.get_or_404(Recipient, token)
    return render_template(
        'recipients/create-edit.html',
        title='Edit a recipient',
        recipient=r,
    )

@recipients_blueprint.post('/<token>')
def update(token):
    r = db.get_or_404(Recipient, token)
    r.last_name = request.form['last_name']
    r.first_name = request.form['first_name']
    r.middle_name = request.form['middle_name']
    r.honorific = request.form['honorific']
    r.suffix = request.form['suffix']
    r.organization = request.form['organization']
    r.address = request.form['address']

    db.session.commit()
    return redirect(url_for('recipients.show', token=r.token))

@recipients_blueprint.post('/<token>/delete')
def delete(token):
    r = db.get_or_404(Recipient, token)
    db.session.delete(r)
    db.session.commit()
    return redirect(url_for(
        'certificates.show',
        id=r.certificate_id,
        messages=['recipient-delete-success'],
    ))

@recipients_blueprint.get('/<token>/overview')
def overview(token):
    return 'Under construction'

@recipients_blueprint.get('/<token>/pdf')
def pdf(token):
    recipient = db.get_or_404(Recipient, token)
    svg_stream = io.BytesIO(recipient_copy_svg_bytestr(recipient))

    pdf_stream = io.BytesIO()
    svg2pdf(file_obj=svg_stream, write_to=pdf_stream)

    filename = f'{recipient.last_name}, {recipient.first_name}.pdf'
    r = Response(pdf_stream.getvalue(), mimetype='application/pdf')
    r.headers['Content-Disposition'] = f'filename="{filename}"'
    return r
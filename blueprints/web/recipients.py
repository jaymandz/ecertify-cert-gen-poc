import io, random, string
from datetime import datetime
from xml.dom.minidom import Text, parse

from cairosvg import svg2pdf, svg2png
from flask import (
    Blueprint, Response, redirect, render_template, request, url_for
)

from models import Certificate, Recipient, db

recipients_blueprint = Blueprint('recipients', __name__)

def complete_name(recipient):
    cn = recipient.last_name
    if recipient.middle_name: cn = f'{recipient.middle_name} {cn}'
    cn = f'{recipient.first_name} {cn}'
    if recipient.honorific: cn = f'{recipient.honorific} {cn}'
    if recipient.suffix: cn += f', {recipient.suffix}'
    return cn

def date_strftime(dv):
    date_format = '%B '+str(dv.day)+', %Y'
    return datetime.strptime(dv, '%Y-%m-%d').strftime(date_format)

def generate_token():
    while True:
        token = ''.join(random.choice(string.ascii_letters) for _ in range(13))
        if not db.session.execute(
            db.select(Recipient).where(Recipient.token==token)
        ).scalar_one_or_none(): break
    return token

def issuance_date_strftime(d):
    ordinal = str(d.day)
    if d.day != 11 and d.day % 10 == 1: ordinal += 'st'
    elif d.day != 12 and d.day % 10 == 2: ordinal += 'nd'
    elif d.day != 13 and d.day % 10 == 3: ordinal += 'rd'
    else: ordinal += 'th'

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
    r.certificate_id = int(request.form['certificate_id'])
    r.token = generate_token()
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
    r = db.get_or_404(Recipient, id)
    return render_template(
        'recipients/show.html',
        title=f'{r.last_name}, {r.first_name}',
        recipient=r,
    )

@recipients_blueprint.get('/<int:id>/edit')
def edit(id):
    r = db.get_or_404(Recipient, id)
    return render_template(
        'recipients/create-edit.html',
        title='Edit a recipient',
        recipient=r,
    )

@recipients_blueprint.post('/<int:id>')
def update(id):
    r = db.get_or_404(Recipient, id)
    r.last_name = request.form['last_name']
    r.first_name = request.form['first_name']
    r.middle_name = request.form['middle_name']
    r.honorific = request.form['honorific']
    r.suffix = request.form['suffix']
    r.organization = request.form['organization']
    r.address = request.form['address']

    db.session.commit()
    return redirect(url_for('recipients.show', id=r.id))

@recipients_blueprint.post('/<int:id>/delete')
def delete(id):
    r = db.get_or_404(Recipient, id)
    db.session.delete(r)
    db.session.commit()
    return redirect(url_for('certificates.show', id=r.certificate_id))

@recipients_blueprint.get('/<int:id>/download/<format>')
def download(id, format):
    recipient = db.get_or_404(Recipient, id)
    template = recipient.certificate.template

    svg_tree = parse(io.StringIO(template.content))
    for t in svg_tree.getElementsByTagName('tspan'):
        if not t.firstChild: continue
        if type(t.firstChild) is not Text: continue

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

    svg_stream = io.BytesIO(svg_tree.toxml(encoding='UTF-8'))

    if format == 'pdf':
        pdf_stream = io.BytesIO()
        svg2pdf(file_obj=svg_stream, write_to=pdf_stream)

        filename = f'{recipient.last_name}, {recipient.first_name}.pdf'
        r = Response(pdf_stream.getvalue(), mimetype='application/pdf')
    elif format == 'png':
        png_stream = io.BytesIO()
        svg2png(file_obj=svg_stream, write_to=png_stream)

        filename = f'{recipient.last_name}, {recipient.first_name}.png'
        r = Response(png_stream.getvalue(), mimetype='image/png')

    r.headers['Content-Disposition'] = f'filename="{filename}"'
    return r
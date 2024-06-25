from enum import Enum

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import LONGTEXT

db = SQLAlchemy()

class FieldValueTypeEnum(Enum):
    text = 'text'
    date = 'date'

class CertificateType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    templates = db.relationship('Template')
    fields = db.relationship('CertificateTypeField')

class CertificateTypeField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    certificate_type_id = db.Column(db.ForeignKey(CertificateType.id))
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    value_type = db.Column(db.Enum(FieldValueTypeEnum))
    is_required = db.Column(db.Boolean())

    certificate_type = db.relationship('CertificateType')

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    certificate_type_id = db.Column(db.ForeignKey(CertificateType.id))
    name = db.Column(db.String(255))
    content = db.Column(
        db.Text().with_variant(LONGTEXT, 'mysql', 'mariadb')
    )

    certificate_type = db.relationship('CertificateType')

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.ForeignKey(Template.id))
    name = db.Column(db.String(255))
    issuance_date = db.Column(db.Date())
    issuance_locale = db.Column(db.String(255))

    template = db.relationship('Template')
    fields = db.relationship('CertificateField')
    recipients = db.relationship('Recipient')

class CertificateField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.ForeignKey(Certificate.id))
    certificate_type_field_id = db.Column(
        db.ForeignKey(CertificateTypeField.id)
    )
    value = db.Column(db.String(255))

    certificate = db.relationship('Certificate')
    certificate_type_field = db.relationship('CertificateTypeField')

class Recipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.ForeignKey(Certificate.id), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    middle_name = db.Column(db.String(255))
    honorific = db.Column(db.String(255))
    suffix = db.Column(db.String(255))
    organization = db.Column(db.String(255))
    address = db.Column(db.String(255))

    certificate = db.relationship('Certificate')
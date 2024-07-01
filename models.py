from enum import Enum

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import LONGTEXT

db = SQLAlchemy()

class FieldValueTypeEnum(Enum):
    text = 'text'
    date = 'date'

class CertificateType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    templates = db.relationship('Template', viewonly=True)
    fields = db.relationship('CertificateTypeField', viewonly=True)

class CertificateTypeField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    certificate_type_id = db.Column(
        db.ForeignKey(CertificateType.id),
        nullable=False,
    )
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    value_type = db.Column(db.Enum(FieldValueTypeEnum), nullable=False)
    is_required = db.Column(db.Boolean(), nullable=False)

    certificate_type = db.relationship('CertificateType')

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    certificate_type_id = db.Column(
        db.ForeignKey(CertificateType.id),
        nullable=False,
    )
    name = db.Column(db.String(255), nullable=False)
    content = db.Column(
        db.Text().with_variant(LONGTEXT, 'mysql', 'mariadb'),
        nullable=False,
    )

    certificate_type = db.relationship('CertificateType')

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.ForeignKey(Template.id), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    issuance_date = db.Column(db.Date(), nullable=False)
    issuance_locale = db.Column(db.String(255), nullable=False)

    template = db.relationship('Template')
    fields = db.relationship('CertificateField', viewonly=True)
    recipients = db.relationship('Recipient', viewonly=True)

class CertificateField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.ForeignKey(Certificate.id), nullable=False)
    certificate_type_field_id = db.Column(
        db.ForeignKey(CertificateTypeField.id),
        nullable=False,
    )
    value = db.Column(db.String(255))

    certificate = db.relationship('Certificate')
    certificate_type_field = db.relationship('CertificateTypeField')

class Recipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.ForeignKey(Certificate.id), nullable=False)
    token = db.Column(db.String(13))
    last_name = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    middle_name = db.Column(db.String(255))
    honorific = db.Column(db.String(255))
    suffix = db.Column(db.String(255))
    organization = db.Column(db.String(255))
    address = db.Column(db.String(255))

    certificate = db.relationship('Certificate')
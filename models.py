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

class CertificateTypeField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    certificate_type = db.Column(db.ForeignKey(CertificateType.id))
    description = db.Column(db.String(255))
    value_type = db.Column(db.Enum(FieldValueTypeEnum))
    is_required = db.Column(db.Boolean())

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    content = db.Column(LONGTEXT)
    # ^ Hopefully I can find a way to create a LONGTEXT in PostgreSQL
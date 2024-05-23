from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    content = db.Column(db.Text())
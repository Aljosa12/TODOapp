from models.settings import db
from datetime import datetime


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    image = db.Column(db.LargeBinary)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship("User")
    created = db.Column(db.String, default=datetime.utcnow)
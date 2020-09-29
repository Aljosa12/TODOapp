from models.settings import db

from datetime import datetime


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship("User")
    created = db.Column(db.String, default=datetime.utcnow)

    def insert(self):
        db.add(self)
        db.commit()

    @property
    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "author": self.author,
            "created": self.created.strftime('%Y-%m-%d'),
        }
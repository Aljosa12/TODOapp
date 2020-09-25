from models.settings import db
from datetime import datetime
import uuid


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    completed = db.Column(db.Integer, default=0)
    image_count = db.Column(db.Integer, default=0)
    password_hash = db.Column(db.String)
    session_token = db.Column(db.String)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, username, password_hash, email):
        session_token = str(uuid.uuid4())

        user = cls(
            username=username,
            password_hash=password_hash,
            session_token=session_token,
            email=email
        )
        db.add(user)
        db.commit()

        return user
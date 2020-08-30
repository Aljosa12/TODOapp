from models.settings import db
from datetime import datetime


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship("User")
    created = db.Column(db.String, default=datetime.utcnow)

    @classmethod
    def read(cls, task_id):
        task = db.query(Task).get(int(task_id))

        return task

    @classmethod
    def read(cls, task_id):
        task = db.query(Task).get(int(task_id))

        return task
import hashlib
import uuid
from itertools import count

from flask import Flask, render_template, request, redirect, url_for, make_response
from datetime import date
from base64 import b64encode

from models.settings import db
from models.users import User
from models.tasks import Task
from models.images import Image

from test import dayNameFromWeekday
from _datetime import datetime, date

app = Flask(__name__)

# create tables in a database (important: this does not update tables, only creates new ones)
db.create_all()


@app.route("/")
def index():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if user:
        return redirect(url_for('tasks'))

    return render_template("index.html", user=user)


@app.route("/logout")
def logout():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    user.session_token = ""
    db.add(user)
    db.commit()

    return redirect(url_for('index'))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if user:
        return redirect(url_for('tasks'))

    if request.method == "GET":
        return render_template("signup.html")

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        repeat = request.form.get("repeat")

        if password != repeat:
            return "Passwords don't match! Go back try again"

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        user = User.create(
            username=username,
            password_hash=password_hash,
            email=email
        )

        response = make_response(redirect(url_for('tasks')))
        response.set_cookie(
            "session_token",
            user.session_token,
            httponly=True,
            samesite='Strict'
        )

        return response


@app.route("/login", methods=["GET", "POST"])
def login():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    if user:
        return redirect(url_for('tasks'))

    if request.method == "GET":
        return render_template("signin.html")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        user = db.query(User).filter_by(username=username).first()

        if not user:
            return "This user does not exist"
        else:
            if password_hash == user.password_hash:
                user.session_token = str(uuid.uuid4())
                db.add(user)
                db.commit()

                response = make_response(redirect(url_for('tasks')))
                response.set_cookie("session_token",
                                    user.session_token,
                                    httponly=True,
                                    samesite='Strict'
                                    )

                return response
            else:
                return "password incorect"


@app.route("/tasks", methods=["GET"])
def tasks():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    img = db.query(Image).filter_by(author_id=user.id).first()

    tasks = db.query(Task).all()
    notification = len(tasks)
    today = str(date.today())

    if not user:
        return redirect(url_for("index"))

    return render_template(
        "tasks.html",
        tasks=tasks,
        user=user,
        today=today,
        img=img,
        notification=notification
    )


@app.route("/my_profile", methods=["GET"])
def my_profile():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    img = db.query(Image).filter_by(author_id=user.id).first()

    if not user:
        return redirect(url_for("index"))

    tasks = db.query(Task).all()
    notification = len(tasks)
    today = date.today()

    this_week_count = 0

    for tsk in tasks:
        if datetime.strptime(tsk.task_date, "%Y-%m-%d").isocalendar()[1] == today.isocalendar()[1]:
            this_week_count = this_week_count + 1

    return render_template("myProfile.html", user=user, img=img, this_week_count=this_week_count, notification=notification)


@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    img = db.query(Image).filter_by(author_id=user.id).first()

    if not user:
        return render_template("index.html")

    if request.method == "GET":
        return render_template("addtask.html", img=img)

    if request.method == "POST":

        text = request.form.get("text")
        notification = len(tasks)
        task_date = request.form.get("date")

        name_day = date.weekday(datetime.strptime(task_date, "%Y-%m-%d"))
        day = dayNameFromWeekday(name_day)

        Task.create(text=text, author=user, day=day, task_date=task_date, notification=notification)

    return redirect(url_for('tasks'))


@app.route("/task/<task_id>/delete", methods=["POST", "GET"])
def task_delete(task_id):
    task = db.query(Task).get(int(task_id))

    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        return "helo"

    if not user:
        return redirect(url_for('login'))

    if request.form['action'] == 'delete':
        task_id = task.id

        db.delete(task)
        db.commit()

    if request.form['action'] == 'completed':
        user.completed += 1
        db.commit()

        task_id = task.id

        db.delete(task)
        db.commit()

    return redirect(url_for('tasks', task_id=task_id))


@app.route("/upload", methods=["POST", "GET"])
def upload():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    img = db.query(Image).filter_by(author_id=user.id).first()

    if request.method == "GET":
        return render_template("uploadImage.html")

    if request.method == "POST":
        if user.image_count >= 1:

            db.delete(img)
            db.commit

        image_url = request.form['image_url']

        newImage = Image(author=user, image_url=image_url)

        user.image_count += 1
        db.commit()

        db.add(newImage)
        db.commit()

        return redirect(url_for('my_profile'))


if __name__ == '__main__':
    app.run()
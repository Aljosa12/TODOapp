import hashlib
import uuid
from flask import Flask, render_template, request, redirect, url_for, make_response
from datetime import date
from base64 import b64encode

from models.settings import db
from models.users import User
from models.tasks import Task
from models.images import Image

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

    today = str(date.today())

    if not user:
        return redirect(url_for("index"))

    tasks = db.query(Task).all()

    return render_template(
        "tasks.html",
        tasks=tasks,
        user=user,
        today=today
    )


@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if not user:
        return render_template("index.html")

    if request.method == "GET":
        return render_template("addtask.html")

    if request.method == "POST":

        text = request.form.get("text")
        day = request.form.get("day")
        date = request.form.get("date")

        Task.create(text=text, author=user, day=day, date=date)

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
        user.completed = user.completed + 1
        db.commit()

        task_id = task.id

        db.delete(task)
        db.commit()

    return redirect(url_for('tasks', task_id=task_id))


@app.route("/upload", methods=["POST", "GET"])
def upload():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        return render_template("uploadImage.html")

    if request.method == "POST":
        file = request.files['inputFile']

        newImage = Image(author=user, name=file.filename, image=file.read())

        db.session.add(newImage)
        db.session.commit()

        return file.filename


if __name__ == '__main__':
    app.run()
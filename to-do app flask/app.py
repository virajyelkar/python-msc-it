import os
from flask import Flask, render_template, request, redirect, url_for
from db_config import db, Task
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

DB_FILE = "tasks.db"

with app.app_context():
    if not os.path.exists(DB_FILE):
        db.create_all()
        print("Database created.")
    else:
        print("Database already exists, skipping creation.")


@app.route("/")
def index():
    pending_tasks = Task.query.filter_by(is_completed=False).order_by(Task.due_date.asc()).all()
    completed_tasks = Task.query.filter_by(is_completed=True).order_by(Task.due_date.asc()).all()
    return render_template("index.html", pending_tasks=pending_tasks, completed_tasks=completed_tasks)


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title")
    description = request.form.get("description")
    priority = request.form.get("priority")
    due_date_str = request.form.get("due_date")
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()

    new_task = Task(
        title=title,
        description=description,
        priority=priority,
        due_date=due_date
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/toggle/<int:id>")
def toggle_task(id):
    task = Task.query.get_or_404(id)
    task.is_completed = not task.is_completed
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/edit/<int:id>")
def edit_task(id):
    task = Task.query.get_or_404(id)
    return render_template("edit.html", task=task)


@app.route("/update/<int:id>", methods=["POST"])
def update_task(id):
    task = Task.query.get_or_404(id)

    task.title = request.form.get("title")
    task.description = request.form.get("description")
    task.priority = request.form.get("priority")
    due_date_str = request.form.get("due_date")
    task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()

    db.session.commit()
    return redirect(url_for("index"))


@app.route("/delete/<int:id>", methods=["POST"])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import Task

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set. Add it to your .env file.")

# Creates tasks.db and the tasks table automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
templates = Jinja2Templates(directory="templates")

PRIORITIES = ("High", "Medium", "Low")
THEMES = ("light", "dark")


# ---------- helpers ----------

class NotLoggedIn(Exception):
    pass


@app.exception_handler(NotLoggedIn)
def not_logged_in_handler(request: Request, exc: NotLoggedIn):
    return RedirectResponse(url="/login", status_code=303)


def get_current_user(request: Request) -> str:
    """Reads the logged-in user's name from the session."""
    user = request.session.get("user")
    if not user:
        raise NotLoggedIn()
    return user


def get_theme(request: Request) -> str:
    """Reads the preferred theme from the cookie (defaults to light)."""
    theme = request.cookies.get("theme", "light")
    return theme if theme in THEMES else "light"


def clean_priority(value: str) -> str:
    return value if value in PRIORITIES else "Medium"


# ---------- LOGIN / LOGOUT ----------

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {
        "theme": get_theme(request),
        "error": None
    })


@app.post("/login")
def login(request: Request, name: str = Form(...)):
    name = name.strip()
    if not name:
        return templates.TemplateResponse(request, "login.html", {
            "theme": get_theme(request),
            "error": "Please enter your name."
        })

    request.session["user"] = name
    return RedirectResponse(url="/", status_code=303)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


# ---------- THEME (cookie) ----------

@app.get("/set-theme/{theme}")
def set_theme(theme: str):
    if theme not in THEMES:
        theme = "light"
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="theme",
        value=theme,
        max_age=60 * 60 * 24 * 365,  # remember for 1 year
        samesite="lax"
    )
    return response


# ---------- TASKS ----------

@app.get("/")
def index(
    request: Request,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    pending_tasks = db.query(Task).filter(
        Task.created_by == user, Task.is_completed == False
    ).order_by(Task.created_at.desc()).all()

    completed_tasks = db.query(Task).filter(
        Task.created_by == user, Task.is_completed == True
    ).order_by(Task.created_at.desc()).all()

    return templates.TemplateResponse(request, "index.html", {
        "theme": get_theme(request),
        "user": user,
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks
    })


@app.post("/add")
def add_task(
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("Medium"),
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    new_task = Task(
        title=title.strip(),
        description=description.strip(),
        priority=clean_priority(priority),
        created_by=user
    )
    db.add(new_task)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/toggle/{id}")
def toggle_task(
    id: int,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == id, Task.created_by == user).first()
    if task:
        task.is_completed = not task.is_completed
        db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/edit/{id}")
def edit_task(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == id, Task.created_by == user).first()
    if not task:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(request, "edit.html", {
        "theme": get_theme(request),
        "task": task
    })


@app.post("/update/{id}")
def update_task(
    id: int,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("Medium"),
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == id, Task.created_by == user).first()
    if task:
        task.title = title.strip()
        task.description = description.strip()
        task.priority = clean_priority(priority)
        db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete/{id}")
def delete_task(
    id: int,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == id, Task.created_by == user).first()
    if task:
        db.delete(task)
        db.commit()
    return RedirectResponse(url="/", status_code=303)
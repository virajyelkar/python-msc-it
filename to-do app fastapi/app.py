from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from database import engine, get_db, Base
from models import Task, User
from auth import hash_password, verify_password, get_current_user, NotAuthenticated, create_access_token

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.exception_handler(NotAuthenticated)
def not_authenticated_handler(request: Request, exc: NotAuthenticated):
    return RedirectResponse(url="/login")


# ---------- AUTH ROUTES ----------

@app.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse(request, "signup.html", {"error": None})


@app.post("/signup")
def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        return templates.TemplateResponse(request, "signup.html", {
            "error": "Username or email already taken."
        })

    new_user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password)
    )
    db.add(new_user)
    db.commit()

    return RedirectResponse(url="/login", status_code=303)


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"error": None})


@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(request, "login.html", {
            "error": "Invalid username or password."
        })

    access_token = create_access_token(data={"sub": str(user.id)})

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60 * 60 * 24,
        samesite="lax"
    )
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response


# ---------- TASK ROUTES (require login) ----------

@app.get("/")
def index(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pending_tasks = db.query(Task).filter(
        Task.user_id == current_user.id, Task.is_completed == False
    ).order_by(Task.due_date.asc()).all()

    completed_tasks = db.query(Task).filter(
        Task.user_id == current_user.id, Task.is_completed == True
    ).order_by(Task.due_date.asc()).all()

    return templates.TemplateResponse(request, "index.html", {
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks,
        "current_user": current_user
    })


@app.post("/add")
def add_task(
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form(...),
    due_date: date = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_task = Task(
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
        user_id=current_user.id
    )
    db.add(new_task)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/toggle/{id}")
def toggle_task(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == id, Task.user_id == current_user.id).first()
    if task:
        task.is_completed = not task.is_completed
        db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/edit/{id}")
def edit_task(id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == id, Task.user_id == current_user.id).first()
    return templates.TemplateResponse(request, "edit.html", {"task": task})


@app.post("/update/{id}")
def update_task(
    id: int,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form(...),
    due_date: date = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == id, Task.user_id == current_user.id).first()
    if task:
        task.title = title
        task.description = description
        task.priority = priority
        task.due_date = due_date
        db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete/{id}")
def delete_task(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == id, Task.user_id == current_user.id).first()
    if task:
        db.delete(task)
        db.commit()
    return RedirectResponse(url="/", status_code=303)
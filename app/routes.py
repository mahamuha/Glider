from typing import Optional
from fastapi import APIRouter, Request, Form, Depends, Query, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from starlette.status import HTTP_303_SEE_OTHER

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_current_user(request: Request, db: Session) -> Optional[models.User]:
    """
    Retrieve the currently authenticated user from the session.

    Args:
        request (Request): Incoming HTTP request.
        db (Session): SQLAlchemy database session.

    Returns:
        Optional[User]: User object if authenticated, otherwise None.
    """
    user_id = request.session.get("user_id")
    if user_id:
        return db.query(models.User).filter(models.User.id == user_id).first()
    return None


@router.get("/")
def home(
    request: Request,
    db: Session = Depends(get_db),
    group_id: Optional[int] = Query(None),
    error: Optional[str] = Query(None)
):
    """
    Render the main homepage with task list, user data, and plant progress.

    Args:
        request (Request): Incoming HTTP request.
        db (Session): Database session dependency.
        group_id (Optional[int]): Group ID to filter tasks by group.
        error (Optional[str]): Optional error message.

    Returns:
        HTMLResponse: Rendered homepage template with context.
    """
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)

    selected_group = db.get(models.Group, group_id) if group_id else None
    user_groups = user.groups

    if selected_group:
        tasks = db.query(models.Task).filter(models.Task.group_id == selected_group.id).all()
        users = selected_group.members
        goal = selected_group.goal or 3
    else:
        tasks = db.query(models.Task).filter(
            models.Task.user_id == user.id,
            models.Task.group_id == None
        ).all()
        users = [user]
        goal = user.goal or 1

    completed_count = len([t for t in tasks if t.completed])
    plant_stage_count = 5

    if goal == 0:
        stage_index = 0
        plant_growth = 0
    elif completed_count >= goal:
        stage_index = plant_stage_count - 1
        plant_growth = 100
    else:
        ratio = completed_count / goal if goal else 0
        stage_index = int(ratio * (plant_stage_count - 1))
        plant_growth = int(ratio * 100)

    plant_image = f"plant_stage_{stage_index + 1}.jpg"

    return templates.TemplateResponse("index.html", {
        "request": request,
        "tasks": tasks,
        "users": users,
        "plant_growth": plant_growth,
        "current_user": user,
        "groups": user_groups,
        "selected_group": selected_group,
        "error": error,
        "plant_image": plant_image
    })


@router.post("/add-task")
def add_task(
    request: Request,
    title: str = Form(...),
    group_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Add a new task to the current user's personal or group list.

    Args:
        request (Request): HTTP request object.
        title (str): Title of the new task.
        group_id (Optional[str]): Group ID, if the task belongs to a group.
        db (Session): Database session.

    Returns:
        RedirectResponse: Redirect to home or group task list.
    """
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)

    group_id_int = int(group_id) if group_id else None
    task = models.Task(title=title, user_id=user.id, group_id=group_id_int)
    db.add(task)
    db.commit()

    redirect_url = f"/?group_id={group_id_int}" if group_id else "/"
    return RedirectResponse(redirect_url, status_code=HTTP_303_SEE_OTHER)


@router.post("/complete-task/{task_id}")
def complete_task(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Mark a task as completed.

    Args:
        task_id (int): ID of the task to be completed.
        request (Request): HTTP request object.
        db (Session): Database session.

    Returns:
        RedirectResponse: Redirect back to current view.
    """
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = True
    db.commit()

    group_id = task.group_id
    redirect_url = f"/?group_id={group_id}" if group_id else "/"
    return RedirectResponse(redirect_url, status_code=HTTP_303_SEE_OTHER)


@router.get("/login")
def login_form(request: Request):
    """
    Render the login form.

    Args:
        request (Request): HTTP request object.

    Returns:
        HTMLResponse: Rendered login page.
    """
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Authenticate or register a user and set session.

    Args:
        request (Request): HTTP request object.
        username (str): Username submitted in the form.
        db (Session): Database session.

    Returns:
        RedirectResponse: Redirect to homepage after login.
    """
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        user = models.User(username=username, password_hash="default", goal=1)
        db.add(user)
        db.commit()
    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)


@router.get("/logout")
def logout(request: Request):
    """
    Log the user out by clearing the session.

    Args:
        request (Request): HTTP request object.

    Returns:
        RedirectResponse: Redirect to login page.
    """
    request.session.clear()
    return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)


@router.post("/create-group")
def create_group(
    request: Request,
    name: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Create a new group or join an existing one by name.

    Args:
        request (Request): HTTP request object.
        name (str): Group name.
        db (Session): Database session.

    Returns:
        RedirectResponse: Redirect to group or homepage with error if any.
    """
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)

    if not name.strip():
        return RedirectResponse(
            "/?error=Group name cannot be empty",
            status_code=HTTP_303_SEE_OTHER
        )

    existing_group = db.query(models.Group).filter(models.Group.name == name).first()
    if existing_group:
        if user in existing_group.members:
            return RedirectResponse(
                f"/?group_id={existing_group.id}&error=Group already exists, you were moved into it.",
                status_code=HTTP_303_SEE_OTHER
            )
        else:
            existing_group.members.append(user)
            db.commit()
            return RedirectResponse(
                f"/?group_id={existing_group.id}&error=You joined the existing group.",
                status_code=HTTP_303_SEE_OTHER
            )

    group = models.Group(name=name, goal=3)
    group.members.append(user)
    db.add(group)
    db.commit()
    db.refresh(group)

    return RedirectResponse(f"/?group_id={group.id}", status_code=HTTP_303_SEE_OTHER)


@router.post("/join-group/{group_id}")
def join_group(
    group_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Join a group by its ID.

    Args:
        group_id (int): ID of the group to join.
        request (Request): HTTP request object.
        db (Session): Database session.

    Returns:
        RedirectResponse: Redirect to group homepage.
    """
    user = get_current_user(request, db)
    group = db.get(models.Group, group_id)
    if user and group and group not in user.groups:
        user.groups.append(group)
        db.commit()
    return RedirectResponse(f"/?group_id={group_id}", status_code=HTTP_303_SEE_OTHER)


@router.post("/set-user-goal")
def set_user_goal(
    request: Request,
    goal: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Set the personal task completion goal for the user.

    Args:
        request (Request): HTTP request object.
        goal (int): Goal value from form.
        db (Session): Database session.

    Returns:
        RedirectResponse: Redirect to homepage.
    """
    user = get_current_user(request, db)
    if user:
        user.goal = goal
        db.commit()
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)


@router.post("/set-group-goal")
def set_group_goal(
    request: Request,
    group_id: int = Form(...),
    goal: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Set the task goal for a specific group.

    Args:
        request (Request): HTTP request object.
        group_id (int): Group ID to set the goal for.
        goal (int): Goal value from form.
        db (Session): Database session.

    Returns:
        RedirectResponse: Redirect to group page.
    """
    user = get_current_user(request, db)
    group = db.get(models.Group, group_id)
    if user and group and user in group.members:
        group.goal = goal
        db.commit()
    return RedirectResponse(f"/?group_id={group_id}", status_code=HTTP_303_SEE_OTHER)

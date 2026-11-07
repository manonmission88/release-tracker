from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .models import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    Task,
    TaskCreate,
    TaskPriority,
    TaskStatus,
    User,
)
from .security import get_password_hash


# this refactor how we communicate with the databases
def slugify(value: str) -> str:
    cleaned = "".join(c for c in value.lower() if c.isalnum() or c == " ")
    return "-".join(cleaned.split()) or "project"


def list_projects(session: Session) -> list[Project]:
    # Express which database records we want.
    statement = select(Project).order_by(Project.name)
    # Use the injected session to retrieve them.
    projects = session.exec(statement).all()
    return projects


def get_project(session: Session, project_id: int) -> Project | None:
    # TODO: Return the Project for `project_id`, or None if it doesn't exist.
    project = session.get(Project, project_id)
    return project


def create_project(session: Session, payload: ProjectCreate, user: User) -> Project | None:
    # TODO: Build a Project from the payload, derive its slug, add/commit/refresh, return it.
    project = Project.model_validate(payload, update={"slug": slugify(payload.name)})
    try:
        session.add(project)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    session.refresh(project)
    return project


def update_project(session: Session, project: Project, payload: ProjectUpdate) -> Project:
    # re-slugify if the name was set, then add/commit/refresh.
    # only use the fields supplied by the client
    updated_fields = payload.model_dump(exclude_unset=True)
    if "name" in updated_fields and not updated_fields["name"]:
        updated_fields["slug"] = slugify(updated_fields["name"])
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def delete_project(session: Session, project: Project, user: User) -> None:
    session.delete(project)
    session.commit()


# for the tasks
def list_tasks(
    session: Session,
    *,
    project_id: int | None = None,
    project_slug: str | None = None,
    task_status: TaskStatus | None = None,
    task_priority: TaskPriority | None = None,
    overdue_only: bool = False,
) -> list[Task]:
    statement = select(Task).options(selectinload(Task.project))  # type: ignore[arg-type]
    if project_id is not None:
        statement = statement.where(Task.project_id == project_id)
    if project_slug is not None:
        statement = statement.join(Project).where(Project.slug == project_slug)
    if task_priority is not None:
        statement = statement.where(Task.priority == task_priority)
    if task_status is not None:
        statement = statement.where(Task.status == task_status)
    if overdue_only:
        statement = statement.where(
            Task.due_date != None,  # noqa: E711
            Task.due_date < datetime.now(UTC).date(),  # type: ignore[operator]
            Task.status != TaskStatus.done,
        )
    return list(session.exec(statement).all())


def get_task(session: Session, task_id: int) -> Task | None:
    statement = select(Task).options(selectinload(Task.project)).where(Task.id == task_id)
    return session.exec(statement).first()


def create_task(session: Session, project_id: int, payload: TaskCreate) -> Task:
    task = Task.model_validate(payload, update={"project_id": project_id})
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def delete_task(session, task):
    session.delete(task)
    session.commit()


def create_user(session: Session, *, email: str, password: str, is_active: bool = True) -> User:
    user = User(
        email=email.lower(),
        hashed_password=get_password_hash(password),
        is_active=is_active,
    )
    session.add(user)
    session.commit()
    return user


def get_user_by_email(session, email_str: str) -> User:
    user = select(User).where(User.email == email_str)
    return session.exec(user).first()

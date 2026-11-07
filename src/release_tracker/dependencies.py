from typing import Annotated

# typing.Annotated, which allows us to attach extra metadata to a type hint. FastAPI is designed to read this metadata.
from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from . import crud
from .database import get_session
from .models import Project, Task, User
from .security import get_current_user

"""

Whenever an API endpoint needs a database session, FastAPI should automatically create or obtain one using get_session() and provide it to that endpoint.
This avoids every endpoint managing its own database

Database Dependency Injection

SessionDep tells FastAPI to provide a database Session
whenever an endpoint declares session: SessionDep.

- Session: The database session type.
- Depends(get_session): Creates/provides the session.
- Annotated: Combines type information with dependency metadata.
- SessionDep: Reusable alias for all database-backed routes.

Flow:
HTTP Request -> get_session() -> Route -> CRUD -> Database

FastAPI also manages session cleanup after the dependency is used.

Benefits:
- Avoids repeating session setup in every endpoint.
- Centralizes database session management.
- Makes it easy to override the database during testing.

"""
CurrentUserDep = Annotated[User, Depends(get_current_user)]
SessionDep = Annotated[Session, Depends(get_session)]


def get_project_404(session: SessionDep, project_id: int) -> Project:
    project = crud.get_project(session, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project Not Found")
    return project


ProjectDep = Annotated[Project, Depends(get_project_404)]


def get_task_or_404(task_id: int, session: SessionDep) -> Task:
    task = crud.get_task(session, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


TaskDep = Annotated[Task, Depends(get_task_or_404)]

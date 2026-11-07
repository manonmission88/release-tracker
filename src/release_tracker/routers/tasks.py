"""
Task API Router

Defines HTTP endpoints for managing tasks associated with projects.

Endpoints:
    GET    /tasks                       - List and filter tasks.
    POST   /projects/{project_id}/tasks - Create a task under a project.
    GET    /tasks/{task_id}             - Retrieve a task.
    PATCH  /tasks/{task_id}             - Update a task.
    DELETE /tasks/{task_id}             - Delete a task.

Dependencies:
    SessionDep - Provides a database session.
    ProjectDep - Retrieves a project or raises HTTP 404.
    TaskDep    - Retrieves a task or raises HTTP 404.

Architecture:
    Client -> APIRouter -> Dependencies -> CRUD -> Database

Responsibilities:
    - Router handles HTTP requests, validation, and responses.
    - Dependencies provide required database objects.
    - CRUD handles database operations.
    - TaskRead defines the API response structure.

APIRouter keeps task endpoints organized and separate from main.py.
"""

from typing import Annotated, Any

from fastapi import APIRouter, Query, Response, status

from .. import crud
from ..dependencies import ProjectDep, SessionDep, TaskDep
from ..models import (
    TaskCreate,
    TaskPriority,
    TaskRead,
    TaskStatus,
)

router = APIRouter(tags=["tasks"])


# get task
@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(session: SessionDep, task: TaskDep) -> Any:
    return task


# list all tasks
@router.get("/tasks/", response_model=list[TaskRead])
def list_tasks(
    session: SessionDep,
    project_id: int | None = None,
    project_slug: str | None = None,
    task_status: Annotated[TaskStatus | None, Query(alias="status")] = None,
    task_priority: Annotated[TaskPriority | None, Query(alias="property")] = None,
    overdue_only: bool = False,
) -> Any:
    return crud.list_tasks(
        session,
        project_id=project_id,
        project_slug=project_slug,
        task_status=task_status,
        task_priority=task_priority,
        overdue_only=overdue_only,
    )


@router.post(
    "/projects/{project_id}/tasks/",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_task(project: ProjectDep, payload: TaskCreate, session: SessionDep):
    return crud.create_task(session, project.id, payload)


# list of takss
@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(session, task):
    crud.delete_task(session, task)
    return Response(status_code=status.HTTP_404_NOT_FOUND)

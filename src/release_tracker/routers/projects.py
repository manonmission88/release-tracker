
"""
APIRouter — PROJECT ROUTES

APIRouter organizes related API endpoints into a separate module
instead of defining every endpoint directly in main.py.

In routers/projects.py:
    - Define router = APIRouter(prefix="/projects", tags=["projects"]).
    - Use @router.get(), @router.post(), @router.patch(),
      and @router.delete() instead of @app.
    - The prefix "/projects" is automatically added to each route.

Dependency Injection:
    - SessionDep provides a database session.
    - ProjectDep retrieves an existing project or raises HTTP 404.
    - FastAPI automatically resolves these dependencies.

Separation of Responsibilities:
    - main.py: Creates the FastAPI app and registers routers.
    - routers/projects.py: Handles HTTP requests and responses.
    - dependencies.py: Provides sessions and existing projects.
    - crud.py: Handles database operations.
    - models.py: Defines data validation and response schemas.

Request Flow:
    Client Request
        -> FastAPI
        -> Project APIRouter
        -> Dependency Injection
        -> CRUD
        -> Database
        -> HTTP Response

Main Benefit:
    APIRouter keeps endpoints modular, reusable, organized,
    and easier to maintain as the application grows.

    Refactoring to APIRouter should not change existing
    endpoint behavior, response models, or HTTP status codes.
    
"""



"""
Putting all our endpoints in main.py works fine for a small project. However, as our application grows to dozens or hundreds of endpoints, main.py becomes hard to navigate and maintain.

FastAPI provides a tool called APIRouter to help us split our application into smaller, focused modules. 
An APIRouter is essentially a "mini-FastAPI" app that we can merge into the main application.




"""
# we can ignore the type check 
from typing import Any 
# The -> Any return type tells static type checkers not to constrain the return value.
from fastapi import APIRouter, status, Response
from .. import crud 
from ..dependencies import ProjectDep, SessionDep
from ..models import ProjectRead, ProjectUpdate,ProjectCreate

router = APIRouter(prefix = "/projects", tags=["projects"])

# SessionDep is required because listing projects needs database access.
# ProjectDep would be incorrect because this endpoint has no project_id.
@router.get("/", response_model=list[ProjectRead])
def list_projects(session: SessionDep) -> Any:
    return crud.list_projects(session)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project: ProjectDep) -> Any:
    return project


@router.post(
    "/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED
)
def create_project(payload: ProjectCreate, session: SessionDep) -> Any:
    # TODO: Call `crud.create_project` with the session and payload, and return the result.
    return crud.create_project(session, payload)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project: ProjectDep, payload: ProjectUpdate, session: SessionDep
) -> Any:
    # Step 1: Fetch the existing project.
    # ProjectDep already fetched the project through get_project_404().
    project = crud.update_project(session, project, payload)

    # Step 2: Return 404 if not found.
    # This check is handled by ProjectDep before the route executes.

    # Step 3: Extract ONLY fields supplied by client.
    #exclude_unset=True ensures we only update fields the client explicitly sent in their request.
    # The actual extraction and update are performed inside crud.update_project().
    return project


# ProjectDep retrieves the existing project using the path parameter.
# SessionDep provides the session needed to delete and commit.
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project: ProjectDep, session: SessionDep) -> Response:
    # TODO: Call `crud.delete_project` with the session and the project, then return a `Response` with `status_code=status.HTTP_204_NO_CONTENT`.
    crud.delete_project(session, project)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


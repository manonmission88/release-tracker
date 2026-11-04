
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, status, Depends, Response, Request
from fastapi.responses import JSONResponse
from .models import ProjectRead, Project, ProjectCreate, ProjectUpdate
from . import crud
from .dependencies import ProjectDep, SessionDep
from sqlalchemy.exc import IntegrityError
from .routers import projects



app = FastAPI(
    title="Release Tracker API",
    description="An API for tracking project milestones and developer tasks"
)

_seed_time = datetime(2026, 1, 1, tzinfo=UTC)

# lets use the new router 
app.include_router(projects.router)

# Declare a reusable requirement:
# "This endpoint needs a database session."
# Expose a public endpoint that returns ProjectRead objects.
"""
By specifying response_model=list[ProjectRead], FastAPI automatically takes the Project database models returned by session.exec(), validates them against our ProjectRead schema, and serializes them to JSON.
We don't have to map the fields ourselves.

"""

"""
FastAPI's @app.exception_handler() decorator solves both problems.
It registers a function that runs whenever a specific exception type bubbles up out of a route, dependency, or anywhere else inside a request.
Routes stay focused on the happy path, crud.py stays free of HTTP knowledge, and the conversion to a 409 happens in one place.

"""

@app.exception_handler(IntegrityError)
def handle_integrity_error(request: Request, exc: IntegrityError):
    # Additional note:
    # This currently treats every IntegrityError as a conflict.
    # In production, distinguish unique violations from other
    # database constraint failures.
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Data Conflict occured (e.g Duplicate Entry)"}
    )


# our project model requires unique slug -> that we will use as part of the URL
# helper function to create the unique slug
"""
In production, use a library like python-slugify to handle special cases like unicode and more.
You'll also need to validate the slug doesn't already exist when updating and creating Project

"""

# root route ("/")
@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "app": "Release Tracker API",
        "docs": "/docs",
        "health": "/health"
    }

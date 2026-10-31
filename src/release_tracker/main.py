from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, status, Depends
from typing import Annotated
from .database import get_session
from sqlmodel import Session,select
from .models import ProjectRead, Project


app = FastAPI(title = "Release Tracker API", description="An API for tracking project milestones and developer tasks")
_seed_time  = datetime(2026,1,1,tzinfo=UTC)
# Declare a reusable requirement:
# "This endpoint needs a database session."
SessionDep = Annotated[Session, Depends(get_session)]

# Expose a public endpoint that returns ProjectRead objects.
"""
By specifying response_model=list[ProjectRead], FastAPI automatically takes the Project database models returned by session.exec(), validates them against our ProjectRead schema, and serializes them to JSON. 
We don't have to map the fields ourselves.

"""

@app.get("/projects", response_model=list[ProjectRead])
def list_projects(session: SessionDep):

    # Express which database records we want.
    statement = select(Project).order_by(Project.name)

    # Use the injected session to retrieve them.
    projects = session.exec(statement).all()

    # Let FastAPI validate and serialize the response.
    return list(projects)

# that for the project path 
# now with the query parameter 
"""
session.get(Model, primary_key) returns the matching row, or None if no row matches. 
We use that None return to raise an HTTP 404 in the route.
"""
@app.get("/projects/{project_id}", response_model= ProjectRead)
def get_project(project_id: int, session: SessionDep):
    # now do the query 
    project = session.get(Project,project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Project Not Found")
    return project


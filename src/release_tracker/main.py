from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, status, Depends, Response
from typing import Annotated
from .database import get_session
from sqlmodel import Session,select
from .models import ProjectRead, Project, ProjectCreate, ProjectUpdate
from sqlalchemy.exc import IntegrityError

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
# our project model requires unique slug -> that we will use as part of the URL 
# helper function to create the unique slug 
"""
In production, use a library like python-slugify to handle special cases like unicode and more. 
You'll also need to validate the slug doesn't already exist when updating and creating Project

"""

def slugify(value: str)->str:
    cleaned = "".join(c for c in value.lower() if c.isalnum() or c == " ")
    return "-".join(cleaned.split()) or "project"

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


"""
POST request
- we need to validate the payload, generate a slug and crea a Project Database 
and commit to the database 
- use post decorator for this 
"""
@app.post("/projects", response_model=ProjectRead, status_code = status.HTTP_201_CREATED)
def create_project(session: SessionDep,payload: ProjectCreate):
    # Create a database model
    project= Project.model_validate(payload,update ={"slug" : slugify(payload.name)})
    # now add project to the session 
    # save to the database 
    # Calling refresh queries the database to populate our Python object with those new, database-generated values so we can return them to the client.
    # what if project already exists 
    try:
        session.add(project)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project name or slug already exists"
        )
        
    session.refresh(project)
    return project

"""
Updating the database 
-> only update the field provided by the client
-> We need to fetch the existing project, update only the changed fields, 
regenerate the slug if the name changed, and commit.

use @patch decorator 
Models:
    ProjectUpdate -> Validates incoming request data.
    Project       -> Represents the database record.
    ProjectRead   -> Defines what data is returned to the client.

"""
@app.patch("/projects/{project_id}", response_model=ProjectRead)
def update_project(session: SessionDep, project_id: int, payload:ProjectUpdate):
     # Step 1: Fetch the existing project.
    project = session.get(Project,project_id)
    # Step 2: Return 404 if not found.
    if not project:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail = "Project Not Found")
    # Step 3: Extract ONLY fields supplied by client.
    #exclude_unset=True ensures we only update fields the client explicitly sent in their request.
    updated_fields = payload.model_dump(exclude_unset=True)
    # Step 4: Regenerate slug when name changes.
    if "name" in updated_fields:
        updated_fields["slug"] = slugify(updated_fields["name"])
        
    #update the database
    session.add(project)
    session.commit()
    session.refresh(project)
    return project 

"""
For delete we neeed which project id we are deleting 

first we read from the database and delete that id from database if exist

"""


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, session: SessionDep):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    session.delete(project)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
                                    


from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, status, Depends, Response, Request
from fastapi.responses import JSONResponse
from .models import ProjectRead, Project, ProjectCreate, ProjectUpdate
from . import crud
from .dependencies import ProjectDep
from sqlalchemy.exc import IntegrityError


app = FastAPI(title = "Release Tracker API", description="An API for tracking project milestones and developer tasks")
_seed_time  = datetime(2026,1,1,tzinfo=UTC)
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
    return JSONResponse(
        status_code = status.HTTP_409_CONFLICT,
        content = {"detail": "Data Conflict occured (e.g Duplicate Entry)"}
    )
# our project model requires unique slug -> that we will use as part of the URL 
# helper function to create the unique slug 
"""
In production, use a library like python-slugify to handle special cases like unicode and more. 
You'll also need to validate the slug doesn't already exist when updating and creating Project

"""

# root route ("/")
@app.get("/")
def read_root() -> dict[str,str]:
    return {
        "app": "Release Tracker API",
        "docs": "/docs",
        "health": "/health"
    }
    

# that for the project path 
# now with the query parameter 
"""
session.get(Model, primary_key) returns the matching row, or None if no row matches. 
We use that None return to raise an HTTP 404 in the route.
"""
@app.get("/projects/{project_id}", response_model= ProjectRead)
def get_project(project: ProjectDep):
    return project


@app.get("/projects", response_model=list[ProjectRead])
def list_projects(project: ProjectDep):
    # Let FastAPI validate and serialize the response.
    return crud.list_projects(project)




"""
POST request
- we need to validate the payload, generate a slug and crea a Project Database 
and commit to the database 
- use post decorator for this 
"""
@app.post("/projects", response_model=ProjectRead, status_code = status.HTTP_201_CREATED)
def create_project(project: ProjectDep,payload: ProjectCreate):
    # Create a database model
    return crud.create_project(project,payload)

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
def update_project(project: ProjectDep, project_id: int, payload:ProjectUpdate):
     # Step 1: Fetch the existing project.
    project = crud.update_project(project,payload)
    # Step 2: Return 404 if not found.
    if not project:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail = "Project Not Found")
    # Step 3: Extract ONLY fields supplied by client.
    #exclude_unset=True ensures we only update fields the client explicitly sent in their request.
    return project 

"""
For delete we neeed which project id we are deleting 

first we read from the database and delete that id from database if exist

"""


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, project: ProjectDep):
    project = crud.get_project(project,project_id) 
    crud.delete_project(ProjectDep,project)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
                                    


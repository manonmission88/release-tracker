from datetime import UTC, datetime, date
from typing import Annotated
from pydantic import StringConstraints
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel, Relationship
from enum import StrEnum




"""
Adding the Task Model
Each project needs a list of tasks with their own state (planned, in progress, done), priority, and an optional due date.

Let's review how to use enum-typed columns and how to build relationships between tables.

Status Enums
We want to restrict status and priority to a fixed set of allowed values.

By using Python enums, we get:

Database enforcement
The API rejecting bad input / unkown values
IDE autocompletes for allowed values
StrEnum is the best fit. Each member compares equal to its string value, which makes serialization to and from JSON easy.

"""
class TaskStatus(StrEnum):
    planned = "planned"
    in_progress = "in_progress"
    blocked = "blocked"
    done = "done"

class TaskPriority(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"
    
TaskTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=2),
]


class TaskBase(SQLModel):
    title: TaskTitle
    details: str | None = None
    status: TaskStatus = TaskStatus.planned
    priority: TaskPriority = TaskPriority.medium
    due_date: date | None = None


class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id", index=True)

    project: Project = Relationship(back_populates="tasks")

class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: TaskTitle | None = None
    details: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None


class TaskRead(TaskBase):
    id: int
    project_id: int

def utc_now()->datetime:
    return datetime.now(UTC)

ProjectName = Annotated[str,StringConstraints(strip_whitespace=True ,min_length = 2)]

class ProjectBase(SQLModel):
    name : ProjectName = Field(unique=True)
    description: str | None = None 

#back_populates="project" tells SQLModel that Project.tasks and Task.project are the two sides of the same relationship.
# Updating one side keeps the other side consistent automatically.
class Project(ProjectBase,table=True):
    __tablename__ = "projects"
    id: int | None = Field(default=None,primary_key=True)
    slug: str = Field(unique=True)
    created_at: datetime = Field(default_factory=utc_now,sa_column=Column(DateTime(timezone=True),nullable = False))
    task: list[Task] = Relationship(back_populates = "project") # making the relationship between task and project table
    
"""

Beyond the database table,API needs schemas that describe hwat clients can send (when creating or updating)

Inherit from projectBase to avoid repeating fields 

"""

class ProjectCreate(ProjectBase):
    pass 

class ProjectUpdate(SQLModel):
    name: ProjectName | None = None 
    descripiton: str | None = None 

class ProjectRead(ProjectBase):
    id: int 
    slug: str 
    created_at: datetime


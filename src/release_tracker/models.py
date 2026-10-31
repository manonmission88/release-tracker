from datetime import UTC, datetime
from typing import Annotated
from pydantic import StringConstraints
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel

def utc_now()->datetime:
    return datetime.now(UTC)

ProjectName = Annotated[str,StringConstraints(strip_whitespace=True ,min_length = 2)]

class ProjectBase(SQLModel):
    name : ProjectName = Field(unique=True)
    description: str | None = None 


class Project(ProjectBase,table=True):
    __tablename__ = "projects"
    id: int | None = Field(default=None,primary_key=True)
    slug: str = Field(unique=True)
    created_at: datetime = Field(default_factory=utc_now,sa_column=Column(DateTime(timezone=True),nullable = False))
    
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


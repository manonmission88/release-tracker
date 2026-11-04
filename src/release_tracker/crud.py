from sqlmodel import Session, select

from .models import Project, ProjectCreate, ProjectUpdate
from sqlalchemy.exc import IntegrityError

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
    project = session.get(Project,project_id)
    return project


def create_project(session: Session, payload: ProjectCreate) -> Project | None:
    # TODO: Build a Project from the payload, derive its slug, add/commit/refresh, return it.
    project= Project.model_validate(payload,update ={"slug" : slugify(payload.name)})
    try:
        session.add(project)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise 
    session.refresh(project)
    return project


def update_project(
    session: Session, project: Project, payload: ProjectUpdate
) -> Project:
    # re-slugify if the name was set, then add/commit/refresh.
    #only use the fields supplied by the client
    updated_fields = payload.model_dump(exclude_unset = True)
    if "name" in updated_fields and not updated_fields["name"]:
        updated_fields["slug"] = slugify(updated_fields["name"])
    session.add(project)
    session.commit()
    session.refresh(project)
    return project 


def delete_project(session: Session, project: Project) -> None:
    session.delete(project)
    session.commit()


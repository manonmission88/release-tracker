from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from .config import get_settings


# database connection happens here
# Create and reuse one database engine.
@lru_cache
def get_engine() -> Engine:
    # Read the database URL from application settings.
    # Example: sqlite:///./database.db
    #
    # create_engine configures the database engine.
    # It does not automatically create database tables.
    return create_engine(get_settings().database_url)


"""
When FastAPI needs to resolve this dependency, it executes the code up until the yield statement.
The with Session(get_engine()) as session: context manager opens a database connection and creates a session, which is then yielded to your route handler.

Once your route handler finishes and returns a response to the user, FastAPI resumes execution of the generator after the yield. At that point, the context manager exits, which automatically closes the database session.

"""


# Provide a database session to API endpoints.
def get_session() -> Generator[Session, None, None]:

    # Open a session using the shared engine.
    with Session(get_engine()) as session:
        # Give the actual session object to FastAPI.
        yield session

    # After the request finishes, the context manager
    # closes the session and releases its resources.

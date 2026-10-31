
from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from .config import get_settings


# Create and reuse one database engine.
@lru_cache
def get_engine() -> Engine:
    # Read the database URL from application settings.
    # Example: sqlite:///./database.db
    #
    # create_engine configures the database engine.
    # It does not automatically create database tables.
    return create_engine(get_settings().database_url)


# Provide a database session to API endpoints.
def get_session() -> Generator[Session, None, None]:

    # Open a session using the shared engine.
    with Session(get_engine()) as session:

        # Give the actual session object to FastAPI.
        yield session

    # After the request finishes, the context manager
    # closes the session and releases its resources.

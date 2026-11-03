import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from release_tracker.main import app
from release_tracker.database import get_session
from release_tracker.models import Project

#mock database 
"""
Code	Purpose
@pytest.fixture	Creates reusable test setup
create_engine("sqlite://")	Creates a temporary in-memory database
SQLModel.metadata.create_all()	Creates test tables
Session(engine)	Connects the session to the test database
dependency_overrides	Makes FastAPI use the test session
yield	Provides the fixture and enables cleanup afterward

"""

@pytest.fixture
def session():
    # Create a fresh SQLite database for each test.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    # Create the database tables.
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


@pytest.fixture
def client(session):
    # Replace the PostgreSQL session dependency.
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_session, None)

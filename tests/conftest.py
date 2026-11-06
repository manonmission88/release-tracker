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
#The fixture in tests/conftest.py gives every test its own clean SQLite instance, 
# an isolated Session, a TestClient wired to override the production session,
# and a few of pre-populated rows for tests that need a starting state.

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

    app.dependency_overrides[get_session] = override_get_session # just duplicate the session 
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_session, None)

#boiler plate code 
@pytest.fixture()
def sample_project_id(client: TestClient) -> int:
    response = client.post(
        "/projects/",
        json={
            "name": "Release Platform",
            "description": "Coordinates planning for the production release.",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.fixture()
def sample_task_id(client: TestClient, sample_project_id: int) -> int:
    response = client.post(
        f"/projects/{sample_project_id}/tasks",
        json={
            "title": "Wire up the dashboard",
            "details": "Connect the API to the static frontend.",
            "status": "planned",
            "priority": "medium",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]

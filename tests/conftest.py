import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from release_tracker.database import get_session
from release_tracker.main import app

# mock database
"""
Code	Purpose
@pytest.fixture	Creates reusable test setup
create_engine("sqlite://")	Creates a temporary in-memory database
SQLModel.metadata.create_all()	Creates test tables
Session(engine)	Connects the session to the test database
dependency_overrides	Makes FastAPI use the test session
yield	Provides the fixture and enables cleanup afterward

"""
# The fixture in tests/conftest.py gives every test its own clean SQLite instance,
# an isolated Session, a TestClient wired to override the production session,
# and a few of pre-populated rows for tests that need a starting state.


@pytest.fixture
def session():
    # Create a fresh SQLite database for each test.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
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

    app.dependency_overrides[get_session] = override_get_session  # just duplicate the session
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_session, None)


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    user = {
        "email": "test@example.com",
        "password": "test@99",
    }

    registered = client.post("/auth/register", json=user)
    assert registered.status_code == 201

    token_response = client.post(
        "/auth/token",
        data={
            "username": user["email"],
            "password": user["password"],
        },
    )
    assert token_response.status_code == 200

    token = token_response.json()["access_token"]
    return {"Authorization": "Bear" + "er " + token}


# boiler plate code
@pytest.fixture()
def sample_project_id(client: TestClient, auth_headers: dict[str, str]) -> int:
    response = client.post(
        "/projects/",
        json={
            "name": "Release Platform",
            "description": "Coordinates planning for the production release.",
        },
        headers=auth_headers,
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

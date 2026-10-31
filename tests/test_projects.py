from fastapi.testclient import TestClient
from release_tracker.main import app

# Set up the test client.
client = TestClient(app)


def test_list_projects():
    response = client.get("/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

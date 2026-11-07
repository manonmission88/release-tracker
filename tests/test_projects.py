from fastapi.testclient import TestClient
from release_tracker.main import app

# Set up the test client.
client = TestClient(app)


def test_list_projects():
    response = client.get("/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# test project with id
def test_get_project():
    response = client.get("/projects/1")
    assert response.status_code == 200
    data = response.json()
    print("Response data", data)
    assert data["id"] == 1


def test_create_project(client: TestClient, auth_headers: dict[str, str]):
    ## The database normally generates the project ID.
    response = client.post(
        "/projects",
        json={"name": "Middleware Apiiiii", "description": "Middleware APII Project"},
        headers=auth_headers,
    )
    print("Response", response.json())
    assert response.status_code == 201


def test_alredy_existed_create_project(
    client: TestClient, auth_headers: dict[str, str]
):
    payload = {
        "name": "Middleware Apiiiii",
        "description": "Middleware APII Project",
    }
    created = client.post(
        "/projects",
        json=payload,
        headers=auth_headers,
    )
    assert created.status_code == 201

    response = client.post("/projects", json=payload, headers=auth_headers)
    assert response.status_code == 409


def test_delete_project(
    client: TestClient, auth_headers: dict[str, str]
):
    client.post(
        "/auth/register",
        json={"email": "delete@example.com", "password": "test@99"},
    )

    token_response = client.post(
        "/auth/token",
        data={
            "username": "delete@example.com",
            "password": "test@99",
        },
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/projects/",
        json={
            "name": "Delete Test Project",
            "description": "Temporary project",
        },
        headers=auth_headers,
    )

    assert created.status_code == 201
    project_id = created.json()["id"]

    # Delete the project.
    response = client.delete(
        f"/projects/{project_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204
    assert response.content == b""

    # Confirm the project no longer exists.
    response = client.get(
        f"/projects/{project_id}"
    )

    assert response.status_code == 404

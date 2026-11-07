from fastapi.testclient import TestClient

from release_tracker.main import app

client = TestClient(app)


# Every fixture in this chapter uses the default function scope, which means a fresh database per test. That's the safest default.
def test_get_task_not_found(client: TestClient):
    response = client.get("/tasks/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_list_tasks_filter_by_status(client: TestClient, sample_project_id: int):
    client.post(
        f"/projects/{sample_project_id}/tasks",
        json={"title": "Planned task", "status": "planned"},
    )
    client.post(
        f"/projects/{sample_project_id}/tasks",
        json={"title": "Done task", "status": "done"},
    )

    response = client.get("/tasks", params={"status": "done"})
    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Done task"]


def test_list_tasks_filter_by_project_slug(client: TestClient, sample_project_id: int, auth_headers: dict[str, str]):
    # TODO: Create a second project, post one task to each project, then
    # GET /tasks?project_slug=<second-project-slug> and assert that only
    # the second project's task comes back.
    other = client.post(
        "/projects/",
        json={"name": "Other Project", "description": "unrelated"},
        headers=auth_headers,
    ).json()
    client.post(f"/projects/{sample_project_id}/tasks", json={"title": "first task"})
    client.post(f"/projects/{other['id']}/tasks", json={"title": "Second task"})
    response = client.get("/tasks", params={"project_slug": other["slug"]})
    assert response.status_code == 200
    assert [task["title"] for task in response.json()]

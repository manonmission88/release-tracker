from fastapi.testclient import TestClient

from release_tracker.main import app

client = TestClient(app)


def test_register_create_users(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={"email": "testemail@gmail.com", "password": "test@99"},
    )
    body = response.json()
    print("===", response.json())
    assert response.status_code == 201
    assert body["email"] == "testemail@gmail.com"
    assert body["is_active"]
    assert "hashed_password" not in body


def test_register_then_login(client: TestClient) -> None:
    # register user
    user_info = {"email": "testmail@gmail.com", "password": "testt@99"}

    login_info = {"username": "testmail@gmail.com", "password": "testt@99"}
    client.post("/auth/register", json=user_info)
    response = client.post(
        "/auth/token",
        data=login_info,
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_register_then_login_wrong_password(client: TestClient) -> None:
    # register user
    user_info = {"email": "testmail@gmail.com", "password": "testt@999"}
    client.post("/auth/register", json=user_info)
    response = client.post(
        "/auth/token",
        data={"username": user_info["email"], "password": "test"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "incorrect email or password"}


def test_register_then_login_wrong_username(client: TestClient) -> None:
    # register user
    user_info = {"email": "testmail@gmail.com", "password": "testt@999"}
    client.post("/auth/register", json=user_info)
    response = client.post(
        "/auth/token",
        data={"username": "test@gmail.com", "password": "test"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "incorrect email or password"}

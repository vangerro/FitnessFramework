from fastapi.testclient import TestClient


def register_user(client: TestClient, *, email: str, password: str) -> dict:
    resp = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()


def login_user(client: TestClient, *, email: str, password: str) -> str:
    resp = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_get_me_requires_auth(client):
    register_user(client, email="a@example.com", password="123456")
    resp = client.get("/users/me")
    assert resp.status_code == 401


def test_get_me_with_token(client):
    user = register_user(client, email="me@example.com", password="123456")
    token = login_user(client, email="me@example.com", password="123456")

    resp = client.get("/users/me", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == user["id"]
    assert data["email"] == user["email"]


def test_get_user_by_id_only_self(client):
    user1 = register_user(client, email="u1@example.com", password="123456")
    user2 = register_user(client, email="u2@example.com", password="123456")
    token1 = login_user(client, email="u1@example.com", password="123456")

    resp = client.get(f"/users/{user1['id']}", headers=auth_headers(token1))
    assert resp.status_code == 200
    assert resp.json()["email"] == user1["email"]

    resp = client.get(f"/users/{user2['id']}", headers=auth_headers(token1))
    assert resp.status_code == 404


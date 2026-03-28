from decimal import Decimal

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


def test_add_weight_and_fetch_sorted(client):
    register_user(client, email="wt@example.com", password="123456")
    token = login_user(client, email="wt@example.com", password="123456")

    client.post(
        "/weight",
        headers=auth_headers(token),
        json={"weight": "80.00", "date": "2026-03-20"},
    )
    client.post(
        "/weight",
        headers=auth_headers(token),
        json={"weight": "79.50", "date": "2026-03-18"},
    )
    client.post(
        "/weight",
        headers=auth_headers(token),
        json={"weight": "81.00", "date": "2026-03-25"},
    )

    resp = client.get("/weight", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert [w["date"] for w in data] == ["2026-03-18", "2026-03-20", "2026-03-25"]
    assert Decimal(str(data[0]["weight"])) == Decimal("79.50")


def test_weight_requires_auth(client):
    register_user(client, email="noauthwt@example.com", password="123456")
    resp = client.get("/weight")
    assert resp.status_code == 401


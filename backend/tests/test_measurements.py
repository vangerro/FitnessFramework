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


def test_add_measurement_and_fetch(client):
    register_user(client, email="m@example.com", password="123456")
    token = login_user(client, email="m@example.com", password="123456")

    client.post(
        "/measurements",
        headers=auth_headers(token),
        json={
            "chest": "100.0",
            "waist": "80.0",
            "arms": "30.0",
            "date": "2026-03-01",
        },
    )
    client.post(
        "/measurements",
        headers=auth_headers(token),
        json={
            "chest": "101.0",
            "waist": "79.0",
            "arms": "30.5",
            "date": "2026-03-15",
        },
    )

    resp = client.get("/measurements", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert [m["date"] for m in data] == ["2026-03-01", "2026-03-15"]
    assert Decimal(str(data[0]["chest"])) == Decimal("100.0")


def test_measurements_require_auth(client):
    resp = client.get("/measurements")
    assert resp.status_code == 401


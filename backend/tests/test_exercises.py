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


def test_add_exercise_and_fetch_workout_with_exercises(client: TestClient):
    register_user(client, email="ex@example.com", password="123456")
    token = login_user(client, email="ex@example.com", password="123456")

    workout = client.post(
        "/workouts",
        headers=auth_headers(token),
        json={"name": "Upper Body", "date": "2026-03-25"},
    ).json()

    created_ex = client.post(
        f"/workouts/{workout['id']}/exercises",
        headers=auth_headers(token),
        json={"name": "Bench Press", "sets": 3, "reps": 10, "weight": "72.50"},
    )
    assert created_ex.status_code == 200
    ex_data = created_ex.json()
    assert ex_data["name"] == "Bench Press"
    assert ex_data["sets"] == 3
    assert ex_data["reps"] == 10

    resp = client.get(
        f"/workouts/{workout['id']}",
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["id"] == workout["id"]
    assert len(detail["exercises"]) == 1
    assert detail["exercises"][0]["name"] == "Bench Press"
    assert Decimal(str(detail["exercises"][0]["weight"])) == Decimal("72.50")


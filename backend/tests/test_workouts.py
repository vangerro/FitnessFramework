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


def test_create_workout(client):
    register_user(client, email="w@example.com", password="123456")
    token = login_user(client, email="w@example.com", password="123456")

    resp = client.post(
        "/workouts",
        headers=auth_headers(token),
        json={"name": "Leg Day", "date": "2026-03-25"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Leg Day"
    assert data["date"] == "2026-03-25"
    assert "id" in data


def test_workouts_require_auth(client):
    register_user(client, email="authz@example.com", password="123456")
    resp = client.get("/workouts")
    assert resp.status_code == 401


def test_fetch_workouts_for_current_user(client):
    register_user(client, email="list@example.com", password="123456")
    token = login_user(client, email="list@example.com", password="123456")

    client.post(
        "/workouts",
        headers=auth_headers(token),
        json={"name": "Workout A", "date": "2026-03-20"},
    )
    client.post(
        "/workouts",
        headers=auth_headers(token),
        json={"name": "Workout B", "date": "2026-03-25"},
    )

    resp = client.get("/workouts", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert [w["name"] for w in data] == ["Workout A", "Workout B"]


def test_delete_workout(client):
    register_user(client, email="del@example.com", password="123456")
    token = login_user(client, email="del@example.com", password="123456")

    created = client.post(
        "/workouts",
        headers=auth_headers(token),
        json={"name": "Delete Me", "date": "2026-03-25"},
    ).json()

    resp = client.delete(
        f"/workouts/{created['id']}",
        headers=auth_headers(token),
    )
    assert resp.status_code == 204

    resp = client.get(f"/workouts/{created['id']}", headers=auth_headers(token))
    assert resp.status_code == 404


def test_workout_access_other_user_returns_404(client):
    user1 = register_user(client, email="u1@example.com", password="123456")
    user2 = register_user(client, email="u2@example.com", password="123456")
    token1 = login_user(client, email="u1@example.com", password="123456")
    token2 = login_user(client, email="u2@example.com", password="123456")

    created = client.post(
        "/workouts",
        headers=auth_headers(token1),
        json={"name": "Secret Workout", "date": "2026-03-25"},
    ).json()

    resp = client.get(f"/workouts/{created['id']}", headers=auth_headers(token2))
    assert resp.status_code == 404


def test_generate_workout_plan_returns_structured_days(client):
    register_user(client, email="generate@example.com", password="123456")
    token = login_user(client, email="generate@example.com", password="123456")

    response = client.post(
        "/workouts/generate",
        headers=auth_headers(token),
        json={
            "days": 3,
            "focus": ["balanced"],
            "periodization": "hypertrophy",
            "experience_level": "intermediate",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "days" in payload
    assert len(payload["days"]) == 3
    assert all(day["day_number"] >= 1 for day in payload["days"])
    assert all(isinstance(day["exercises"], list) for day in payload["days"])
    assert all(day["exercises"] for day in payload["days"])


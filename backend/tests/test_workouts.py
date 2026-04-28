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


def test_generate_workout_plan_rejects_more_than_five_days(client):
    register_user(client, email="generate-limit@example.com", password="123456")
    token = login_user(client, email="generate-limit@example.com", password="123456")

    response = client.post(
        "/workouts/generate",
        headers=auth_headers(token),
        json={
            "days": 6,
            "focus": ["balanced"],
            "periodization": "hypertrophy",
            "experience_level": "intermediate",
        },
    )
    assert response.status_code == 422


def test_save_plan_and_manage_named_workout_plan(client):
    register_user(client, email="plan-owner@example.com", password="123456")
    token = login_user(client, email="plan-owner@example.com", password="123456")

    generated = client.post(
        "/workouts/generate",
        headers=auth_headers(token),
        json={
            "days": 3,
            "focus": ["balanced"],
            "periodization": "hypertrophy",
            "experience_level": "intermediate",
        },
    )
    assert generated.status_code == 200
    generated_days = generated.json()["days"]

    save_resp = client.post(
        "/workouts/save-plan",
        headers=auth_headers(token),
        json={"name": "Push Pull Base", "days": generated_days},
    )
    assert save_resp.status_code == 200
    save_payload = save_resp.json()
    assert "plan_id" in save_payload
    assert len(save_payload["created_workout_ids"]) == 3

    plans_resp = client.get("/workouts/plans", headers=auth_headers(token))
    assert plans_resp.status_code == 200
    plans = plans_resp.json()
    assert len(plans) == 1
    assert plans[0]["name"] == "Push Pull Base"
    assert plans[0]["workout_count"] == 3

    detail_resp = client.get(
        f"/workouts/plans/{save_payload['plan_id']}",
        headers=auth_headers(token),
    )
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["name"] == "Push Pull Base"
    assert len(detail["workouts"]) == 3
    assert all("exercises" in workout for workout in detail["workouts"])
    first_exercise = detail["workouts"][0]["exercises"][0]
    assert len(first_exercise["targets"]) == first_exercise["sets"]

    rename_resp = client.patch(
        f"/workouts/plans/{save_payload['plan_id']}",
        headers=auth_headers(token),
        json={"name": "Updated Plan Name"},
    )
    assert rename_resp.status_code == 200
    assert rename_resp.json()["name"] == "Updated Plan Name"

    delete_resp = client.delete(
        f"/workouts/plans/{save_payload['plan_id']}",
        headers=auth_headers(token),
    )
    assert delete_resp.status_code == 204

    after_delete_resp = client.get(
        f"/workouts/plans/{save_payload['plan_id']}",
        headers=auth_headers(token),
    )
    assert after_delete_resp.status_code == 404


def test_log_workout_session_with_set_logs(client):
    register_user(client, email="session-owner@example.com", password="123456")
    token = login_user(client, email="session-owner@example.com", password="123456")

    generated = client.post(
        "/workouts/generate",
        headers=auth_headers(token),
        json={
            "days": 2,
            "focus": ["balanced"],
            "periodization": "hypertrophy",
            "experience_level": "intermediate",
        },
    )
    assert generated.status_code == 200
    generated_days = generated.json()["days"]

    save_resp = client.post(
        "/workouts/save-plan",
        headers=auth_headers(token),
        json={"name": "Session Plan", "days": generated_days},
    )
    assert save_resp.status_code == 200
    plan_id = save_resp.json()["plan_id"]

    detail_resp = client.get(f"/workouts/plans/{plan_id}", headers=auth_headers(token))
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    workout = detail["workouts"][0]
    exercise = workout["exercises"][0]

    set_logs = []
    for set_number in range(1, exercise["sets"] + 1):
        set_logs.append(
            {
                "exercise_id": exercise["id"],
                "set_number": set_number,
                "reps": exercise["reps"],
                "weight": "40",
            }
        )

    session_resp = client.post(
        f"/workouts/plans/{plan_id}/workouts/{workout['id']}/sessions",
        headers=auth_headers(token),
        json={"set_logs": set_logs},
    )
    assert session_resp.status_code == 200
    session = session_resp.json()
    assert session["workout_id"] == workout["id"]
    assert len(session["set_logs"]) == exercise["sets"]

    list_sessions_resp = client.get(
        f"/workouts/plans/{plan_id}/workouts/{workout['id']}/sessions",
        headers=auth_headers(token),
    )
    assert list_sessions_resp.status_code == 200
    sessions = list_sessions_resp.json()
    assert len(sessions) == 1
    assert sessions[0]["id"] == session["id"]
    assert len(sessions[0]["set_logs"]) == exercise["sets"]

    detail_after_resp = client.get(f"/workouts/plans/{plan_id}", headers=auth_headers(token))
    assert detail_after_resp.status_code == 200
    detail_after = detail_after_resp.json()
    assert detail_after["recent_sessions"]
    assert detail_after["recent_sessions"][0]["workout_id"] == workout["id"]


def test_update_exercise_targets(client):
    register_user(client, email="target-owner@example.com", password="123456")
    token = login_user(client, email="target-owner@example.com", password="123456")

    generated = client.post(
        "/workouts/generate",
        headers=auth_headers(token),
        json={
            "days": 2,
            "focus": ["balanced"],
            "periodization": "hypertrophy",
            "experience_level": "intermediate",
        },
    )
    assert generated.status_code == 200

    save_resp = client.post(
        "/workouts/save-plan",
        headers=auth_headers(token),
        json={"name": "Targets Plan", "days": generated.json()["days"]},
    )
    assert save_resp.status_code == 200
    plan_id = save_resp.json()["plan_id"]

    detail_resp = client.get(f"/workouts/plans/{plan_id}", headers=auth_headers(token))
    assert detail_resp.status_code == 200
    exercise = detail_resp.json()["workouts"][0]["exercises"][0]
    assert exercise["targets"]

    updated_targets = [
        {
            "set_number": target["set_number"],
            "planned_reps": target["planned_reps"] + 1,
            "planned_weight": "22.5",
        }
        for target in exercise["targets"]
    ]
    replace_resp = client.put(
        f"/workouts/plans/{plan_id}/exercises/{exercise['id']}/targets",
        headers=auth_headers(token),
        json={"targets": updated_targets},
    )
    assert replace_resp.status_code == 200
    replace_payload = replace_resp.json()
    assert replace_payload["exercise_id"] == exercise["id"]
    assert len(replace_payload["targets"]) == len(updated_targets)

    detail_after_resp = client.get(f"/workouts/plans/{plan_id}", headers=auth_headers(token))
    assert detail_after_resp.status_code == 200
    exercise_after = detail_after_resp.json()["workouts"][0]["exercises"][0]
    assert [item["planned_reps"] for item in exercise_after["targets"]] == [
        item["planned_reps"] for item in updated_targets
    ]
    assert all(str(item["planned_weight"]) in {"22.5", "22.50"} for item in exercise_after["targets"])


def test_workout_plan_routes_are_user_scoped(client):
    register_user(client, email="scope-a@example.com", password="123456")
    register_user(client, email="scope-b@example.com", password="123456")
    token_a = login_user(client, email="scope-a@example.com", password="123456")
    token_b = login_user(client, email="scope-b@example.com", password="123456")

    generated = client.post(
        "/workouts/generate",
        headers=auth_headers(token_a),
        json={
            "days": 2,
            "focus": ["balanced"],
            "periodization": "hypertrophy",
            "experience_level": "intermediate",
        },
    )
    assert generated.status_code == 200
    generated_days = generated.json()["days"]

    save_resp = client.post(
        "/workouts/save-plan",
        headers=auth_headers(token_a),
        json={"name": "Private Plan", "days": generated_days},
    )
    assert save_resp.status_code == 200
    plan_id = save_resp.json()["plan_id"]

    detail_a = client.get(f"/workouts/plans/{plan_id}", headers=auth_headers(token_a))
    assert detail_a.status_code == 200
    workout_id = detail_a.json()["workouts"][0]["id"]
    exercise_id = detail_a.json()["workouts"][0]["exercises"][0]["id"]

    assert client.get(f"/workouts/plans/{plan_id}", headers=auth_headers(token_b)).status_code == 404
    assert (
        client.patch(
            f"/workouts/plans/{plan_id}",
            headers=auth_headers(token_b),
            json={"name": "Hacked"},
        ).status_code
        == 404
    )
    assert (
        client.delete(f"/workouts/plans/{plan_id}", headers=auth_headers(token_b)).status_code
        == 404
    )
    assert (
        client.post(
            f"/workouts/plans/{plan_id}/workouts/{workout_id}/sessions",
            headers=auth_headers(token_b),
            json={
                "set_logs": [
                    {
                        "exercise_id": exercise_id,
                        "set_number": 1,
                        "reps": 10,
                        "weight": "20",
                    }
                ]
            },
        ).status_code
        == 404
    )
    assert (
        client.get(
            f"/workouts/plans/{plan_id}/workouts/{workout_id}/sessions",
            headers=auth_headers(token_b),
        ).status_code
        == 404
    )
    assert (
        client.put(
            f"/workouts/plans/{plan_id}/exercises/{exercise_id}/targets",
            headers=auth_headers(token_b),
            json={"targets": [{"set_number": 1, "planned_reps": 10, "planned_weight": "30"}]},
        ).status_code
        == 404
    )

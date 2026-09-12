"""Integration tests for FastAPI REST API endpoints."""

import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_problems_endpoint():
    response = client.get("/api/v1/problems")
    assert response.status_code == 200
    problems = response.json()
    assert len(problems) == 3
    slugs = [p["slug"] for p in problems]
    assert "parking-lot" in slugs
    assert "elevator-system" in slugs
    assert "vending-machine" in slugs


def test_get_single_problem():
    response = client.get("/api/v1/problems/parking-lot")
    assert response.status_code == 200
    p = response.json()
    assert p["slug"] == "parking-lot"
    assert "starter_code" in p
    assert len(p["functional_requirements"]) > 0


def test_attempt_draft_and_submission_workflow():
    # 1. Start attempt
    start_resp = client.post("/api/v1/attempts", json={"problem_id": "parking-lot"})
    assert start_resp.status_code == 200
    attempt_data = start_resp.json()
    attempt_id = attempt_data["id"]

    # 2. Auto-save draft
    save_resp = client.put(
        f"/api/v1/attempts/{attempt_id}",
        json={
            "code": attempt_data["code"] + "\n# added test comment",
            "design_notes": "# Updated design rationale",
            "diagram_dsl": attempt_data["diagram_dsl"],
        },
    )
    assert save_resp.status_code == 200
    assert save_resp.json()["draft_version"] >= 2

    # 3. Submit
    submit_resp = client.post(f"/api/v1/attempts/{attempt_id}/submit")
    assert submit_resp.status_code == 200
    sub_data = submit_resp.json()
    sub_id = sub_data["id"]
    assert sub_data["status"] in ("SUBMITTED", "PENDING", "EVALUATING")


    # 4. Poll until completed (max 15s)
    completed = False
    for _ in range(30):
        time.sleep(0.5)
        poll_resp = client.get(f"/api/v1/submissions/{sub_id}")
        assert poll_resp.status_code == 200
        poll_data = poll_resp.json()
        if poll_data["status"] == "COMPLETED":
            completed = True
            assert poll_data["evaluation"] is not None
            assert poll_data["evaluation"]["overall_score"] > 0
            break
        elif poll_data["status"] == "FAILED":
            break

    assert completed, f"Submission did not complete within expected timeout. Current status: {poll_data.get('status')}, error: {poll_data.get('error_message')}"


def test_dashboard_stats_endpoint():
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "metrics" in stats
    assert "candidate_profile" in stats
    assert "skill_radar" in stats

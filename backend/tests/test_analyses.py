from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.redis_state import ANALYSIS_CHANNEL, set_analysis_state

client = TestClient(app)

def test_create_analysis():
    response = client.post(
        "/api/v1/analyses",
        json={
            "repository_path": "./compiler",
            "limit": 5
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "queued"
    assert "analysis_id" in data
    assert "job_id" in data

def test_create_analysis_invalid_request():
    response = client.post(
        "/api/v1/analyses",
        json={
            "repository_path": "",
            "limit": 0
        }
    )

    assert response.status_code == 422

def test_inspect_redis():
    analysis_id = "test-api-inspector"

    set_analysis_state(
        analysis_id=analysis_id,
        status="running",
        stage="analysis",
        progress=20,
    )

    response = client.get(
        f"/api/v1/redis/inspector/{analysis_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["state"]["analysis_id"] == analysis_id
    assert data["state"]["state"]["status"] == "running"
    assert data["state"]["state"]["stage"] == "analysis"
    assert data["state"]["state"]["progress"] == "20"
    assert data["state"]["ttl"] > 0

    assert data["queue"]["queue"] == "analysis"
    assert "waiting" in data["queue"]["counts"]
    assert "active" in data["queue"]["counts"]

    assert data["channel"]["channel"] == ANALYSIS_CHANNEL
    assert data["channel"]["subscribers"] >= 0
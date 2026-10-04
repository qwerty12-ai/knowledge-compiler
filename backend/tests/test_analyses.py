from fastapi.testclient import TestClient
from backend.app.main import app

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

    assert data["schema_version"] == "1.0"
    assert data["files_discovered"] > 0
    assert data["limit"] == 5
    assert isinstance(data["claims"], list)
    assert isinstance(data["evidence"], list)
    assert data["errors"] == []

def test_create_analysis_invalid_request():
    response = client.post(
        "/api/v1/analyses",
        json={
            "repository_path": "",
            "limit": 0
        }
    )

    assert response.status_code == 422
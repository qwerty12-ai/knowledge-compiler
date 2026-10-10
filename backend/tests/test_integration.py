import time
import pytest
import requests
import os

API_URL = "http://localhost:8000"

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_DOCKER_AI_INTEGRATION", "1") == "0",
    reason="Requires the Docker stack and configured AI provider",
)

def wait_for_analysis(analysis_id: str, timeout: int = 300) -> dict:
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        response = requests.get(
            f"{API_URL}/api/v1/analyses/{analysis_id}",
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()

        if result["status"] == "completed":
            return result

        if result["status"] == "failed":
            pytest.fail(
                f"Analysis {analysis_id} failed: {result}"
            )

        time.sleep(2)

    pytest.fail(
        f"Analysis {analysis_id} did not complete "
        f"within {timeout} seconds."
    )


def test_full_analysis_pipeline():
    # Confirm the real Docker API is available.
    health = requests.get(f"{API_URL}/health", timeout=10)
    health.raise_for_status()
    assert health.json()["status"] == "ok"

    response = requests.post(
        f"{API_URL}/api/v1/analyses",
        json={
            "repository_path": (
                "/workspace/knowledge-compiler/compiler"
            ),
            "limit": 1,
            "with_ai": True,
        },
        timeout=15,
    )
    response.raise_for_status()

    created = response.json()
    analysis_id = created["analysis_id"]

    assert created["status"] == "queued"
    assert created["job_id"]

    final_state = wait_for_analysis(analysis_id)

    assert final_state["status"] == "completed"

    claims_response = requests.get(
        f"{API_URL}/api/v1/analyses/{analysis_id}/claims",
        timeout=15,
    )
    claims_response.raise_for_status()
    claims = claims_response.json()

    assert claims["analysis_id"] == analysis_id
    assert isinstance(claims["claims"], list)

    evidence_response = requests.get(
        f"{API_URL}/api/v1/analyses/{analysis_id}/evidence",
        timeout=15,
    )
    evidence_response.raise_for_status()
    evidence = evidence_response.json()

    assert evidence["analysis_id"] == analysis_id
    assert isinstance(evidence["evidence"], list)
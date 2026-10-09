from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database import get_database_connection
from backend.app.services.redis_state import ANALYSIS_CHANNEL, set_analysis_state
from backend.app.services.persistence import (
    save_analysis,
    save_evidence,
    save_claims,
    save_claim_evidence,
)
from backend.app.services.results import get_analysis

from knowledge_compiler.models import Evidence, Claim
from knowledge_compiler.output import AnalysisResult

from .test_persistence import delete_analysis

client = TestClient(app)

def create_test_analysis():
    result = AnalysisResult(
        schema_version="1.0",
        repository=str(Path("./compiler").resolve()),
        files_discovered=28,
        with_ai=False,
        limit=5,
        claims=(),
        evidence=(),
        errors=(),
    )

    return save_analysis(result)

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

def test_get_analysis_status():
    analysis_id = "test-analysis-status"

    set_analysis_state(
        analysis_id=analysis_id,
        status="running",
        stage="analysis",
        progress=20,
    )

    response = client.get(
        f"/api/v1/analyses/{analysis_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["analysis_id"] == analysis_id
    assert data["status"] == "running"
    assert data["stage"] == "analysis"
    assert data["progress"] == 20

def test_get_analysis_claims():
    analysis_id = create_test_analysis()

    try:
        claims = [
            Claim(
                statement="The repository contains Python source code.",
                status="VERIFIED",
                confidence=0.95,
                evidence=[],
            ),
            Claim(
                statement="The repository contains automated tests.",
                status="SUPPORTED",
                confidence=0.85,
                evidence=[],
            ),
        ]

        claim_ids = save_claims(analysis_id, claims)

        response = client.get(
            f"/api/v1/analyses/{analysis_id}/claims"
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data["claims"]) == 2
        assert data["claims"][0]["id"] == claim_ids[0]
        assert data["claims"][0]["statement"] == claims[0].statement
        assert data["claims"][0]["status"] == "VERIFIED"

        assert data["claims"][1]["id"] == claim_ids[1]
        assert data["claims"][1]["statement"] == claims[1].statement

    finally:
        delete_analysis(analysis_id)


def test_get_claim_detail():
    analysis_id = create_test_analysis()

    try:
        evidence = [
            Evidence(
                source=Path("compiler/src/example.py"),
                kind="file_content",
                description="File contains source code.",
                language="python",
                content="print('hello')",
                line_start=1,
                line_end=1,
            ),
            Evidence(
                source=Path("compiler/tests/test_example.py"),
                kind="test",
                description="File contains an automated test.",
                language="python",
                content="def test_example():",
                line_start=1,
                line_end=1,
            ),
        ]

        evidence_ids = save_evidence(analysis_id, evidence)

        claims = [
            Claim(
                statement="The repository contains Python source code.",
                status="VERIFIED",
                confidence=0.95,
                evidence=[],
            )
        ]

        claim_ids = save_claims(analysis_id, claims)

        save_claim_evidence(
            claim_id=claim_ids[0],
            evidence_ids=evidence_ids,
        )

        response = client.get(
            f"/api/v1/claims/{claim_ids[0]}"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == claim_ids[0]
        assert data["analysis_id"] == analysis_id
        assert data["statement"] == claims[0].statement
        assert data["status"] == "VERIFIED"
        assert len(data["evidence"]) == 2

        assert data["evidence"][0]["id"] == evidence_ids[0]
        assert data["evidence"][1]["id"] == evidence_ids[1]

    finally:
        delete_analysis(analysis_id)


def test_get_analysis_evidence():
    analysis_id = create_test_analysis()

    try:
        evidence = [
            Evidence(
                source=Path("compiler/src/example.py"),
                kind="file_content",
                description="File contains source code.",
                language="python",
                content="print('hello')",
                line_start=1,
                line_end=1,
            ),
            Evidence(
                source=Path("compiler/tests/test_example.py"),
                kind="test",
                description="File contains an automated test.",
                language="python",
                content="def test_example():",
                line_start=1,
                line_end=1,
            ),
        ]

        evidence_ids = save_evidence(analysis_id, evidence)

        response = client.get(
            f"/api/v1/analyses/{analysis_id}/evidence"
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data["evidence"]) == 2

        assert data["evidence"][0]["id"] == evidence_ids[0]
        assert data["evidence"][0]["source"] == str(evidence[0].source)
        assert data["evidence"][0]["kind"] == "file_content"

        assert data["evidence"][1]["id"] == evidence_ids[1]
        assert data["evidence"][1]["source"] == str(evidence[1].source)
        assert data["evidence"][1]["kind"] == "test"

        assert "content" not in data["evidence"][0]
        assert "content" not in data["evidence"][1]

    finally:
        delete_analysis(analysis_id)


def test_get_analysis_history():
    analysis_id = create_test_analysis()

    try:
        claims = [
            Claim(
                statement="The repository contains Python source code.",
                status="VERIFIED",
                confidence=0.95,
                evidence=[],
            )
        ]

        claim_ids = save_claims(analysis_id, claims)

        evidence = [
            Evidence(
                source=Path("compiler/src/example.py"),
                kind="file_content",
                description="File contains source code.",
                language="python",
                content="print('hello')",
                line_start=1,
                line_end=1,
            )
        ]

        evidence_ids = save_evidence(analysis_id, evidence)

        save_claim_evidence(
            claim_id=claim_ids[0],
            evidence_ids=evidence_ids,
        )

        response = client.get("/api/v1/analyses")

        assert response.status_code == 200

        data = response.json()

        analysis = next(
            item for item in data["analyses"]
            if item["id"] == analysis_id
        )

        assert analysis["repository_path"] == str(
            Path("./compiler").resolve()
        )
        assert analysis["files_discovered"] == 28
        assert analysis["claims_count"] == 1
        assert analysis["evidence_count"] == 1

    finally:
        delete_analysis(analysis_id)


def test_get_analysis_status_from_database():
    analysis_id = create_test_analysis()

    try:
        response = client.get(
            f"/api/v1/analyses/{analysis_id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["analysis_id"] == str(analysis_id)
        assert data["status"] == "completed"
        assert data["progress"] == 100
        assert data["database_id"] == analysis_id

    finally:
        delete_analysis(analysis_id)
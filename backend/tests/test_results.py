from pathlib import Path
from decimal import Decimal

from backend.app.database import get_database_connection
from backend.app.services.persistence import (
    save_analysis,
    save_evidence,
    save_claims,
    save_claim_evidence,
)
from backend.app.services.results import (
    get_analysis_claims,
    get_claim_with_evidence,
    get_analysis_evidence,
    get_recent_analyses,
    get_analysis,
)
from knowledge_compiler.models import Evidence, Claim
from knowledge_compiler.output import AnalysisResult
from .test_persistence import delete_analysis


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

        result = get_analysis_claims(analysis_id)

        assert len(result) == 2
        assert result[0]["id"] == claim_ids[0]
        assert result[0]["statement"] == claims[0].statement
        assert result[0]["status"] == "VERIFIED"
        assert result[0]["confidence"] == Decimal("0.950")

        assert result[1]["id"] == claim_ids[1]
        assert result[1]["statement"] == claims[1].statement

    finally:
        delete_analysis(analysis_id)


def test_get_claim_with_evidence():
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

        result = get_claim_with_evidence(claim_ids[0])

        assert result is not None
        assert result["id"] == claim_ids[0]
        assert result["analysis_id"] == analysis_id
        assert result["statement"] == claims[0].statement
        assert result["status"] == "VERIFIED"
        assert result["confidence"] == Decimal("0.950")

        assert len(result["evidence"]) == 2
        assert result["evidence"][0]["id"] == evidence_ids[0]
        assert result["evidence"][1]["id"] == evidence_ids[1]

    finally:
        delete_analysis(analysis_id)


def test_get_claim_with_evidence_not_found():
    result = get_claim_with_evidence(999999999)

    assert result is None


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

        result = get_analysis_evidence(analysis_id)

        assert len(result) == 2
        assert result[0]["id"] == evidence_ids[0]
        assert result[0]["source"] == str(evidence[0].source)
        assert result[0]["kind"] == "file_content"

        assert result[1]["id"] == evidence_ids[1]
        assert result[1]["source"] == str(evidence[1].source)
        assert result[1]["kind"] == "test"

        assert "content" not in result[0]
        assert "content" not in result[1]

    finally:
        delete_analysis(analysis_id)


def test_get_recent_analyses():
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

        result = get_recent_analyses(limit=10)

        analysis = next(
            item for item in result
            if item["id"] == analysis_id
        )

        assert analysis["repository_path"] == str(
            Path("./compiler").resolve()
        )
        assert analysis["schema_version"] == "1.0"
        assert analysis["files_discovered"] == 28
        assert analysis["with_ai"] == 0
        assert analysis["analysis_limit"] == 5
        assert analysis["claims_count"] == 1
        assert analysis["evidence_count"] == 1

    finally:
        delete_analysis(analysis_id)


def test_get_analysis():
    analysis_id = create_test_analysis()

    try:
        result = get_analysis(analysis_id)

        assert result is not None
        assert result["id"] == analysis_id
        assert result["repository_path"] == str(
            Path("./compiler").resolve()
        )
        assert result["schema_version"] == "1.0"
        assert result["files_discovered"] == 28
        assert result["with_ai"] == 0
        assert result["analysis_limit"] == 5

    finally:
        delete_analysis(analysis_id)


def test_get_analysis_not_found():
    result = get_analysis(999999999)

    assert result is None
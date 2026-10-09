from pathlib import Path
from backend.app.services.persistence import save_analysis, save_evidence, save_claims, save_claim_evidence
from backend.app.database import get_database_connection
from knowledge_compiler.output import AnalysisResult
from knowledge_compiler.models import Evidence, Claim

def delete_analysis(analysis_id: int) -> None:
    connection= get_database_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM analyses WHERE id = %s", (analysis_id,))
        connection.commit()
        cursor.close()
    finally:
        connection.close()

def test_save_analysis():
    result = AnalysisResult(
        schema_version="1.0",
        repository=str(Path("./compiler").resolve()),
        files_discovered=28,
        with_ai=False,
        limit=5,
        claims=(),
        evidence=(),
        errors=()
    )

    analysis_id = save_analysis(result)

    try:
        assert analysis_id is not None
        assert analysis_id > 0
    finally:
        delete_analysis(analysis_id)


def test_save_evidence():
    result = AnalysisResult(
        schema_version="1.0",
        repository=str(Path("./compiler").resolve()),
        files_discovered=28,
        with_ai=False,
        limit=5,
        claims=(),
        evidence=(),
        errors=()
    )

    analysis_id = save_analysis(result)

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

        assert len(evidence_ids) == 2
        assert all(id > 0 for id in evidence_ids)

        connection = get_database_connection()

        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM evidence WHERE analysis_id = %s",
                (analysis_id,),
            )
            count = cursor.fetchone()[0]

            assert count == 2

            cursor.close()

        finally:
            connection.close()

    finally:
        delete_analysis(analysis_id)


def test_save_claims():
    result = AnalysisResult(
        schema_version="1.0",
        repository=str(Path("./compiler").resolve()),
        files_discovered=28,
        with_ai=False,
        limit=5,
        claims=(),
        evidence=(),
        errors=()
    )

    analysis_id = save_analysis(result)

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

        assert len(claim_ids) == 2
        assert all(id > 0 for id in claim_ids)

        connection = get_database_connection()

        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM claims WHERE analysis_id = %s",
                (analysis_id,),
            )
            count = cursor.fetchone()[0]

            assert count == 2

            cursor.close()

        finally:
            connection.close()

    finally:
        delete_analysis(analysis_id)


def test_save_claim_evidence():
    result = AnalysisResult(
        schema_version="1.0",
        repository=str(Path("./compiler").resolve()),
        files_discovered=28,
        with_ai=False,
        limit=5,
        claims=(),
        evidence=(),
        errors=()
    )

    analysis_id = save_analysis(result)

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

        connection = get_database_connection()

        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM claim_evidence WHERE claim_id = %s",
                (claim_ids[0],),
            )
            count = cursor.fetchone()[0]

            assert count == 2

            cursor.close()

        finally:
            connection.close()

    finally:
        delete_analysis(analysis_id)
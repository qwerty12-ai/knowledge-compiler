from pathlib import Path

from knowledge_compiler.claims import generate_claims
from knowledge_compiler.models import Evidence


def test_generate_claim_from_file_content(tmp_path: Path):
    file_path = tmp_path / "example.py"
    file_path.write_text("print('hello')\n")

    evidence = Evidence(
        source=file_path,
        kind="file_content",
        description="File contains 1 lines of source code.",
    )

    claims = generate_claims([evidence])

    assert len(claims) == 1
    assert claims[0].statement == (
        "The repository contains source code in example.py."
    )
    assert claims[0].evidence == (evidence,)
    assert claims[0].confidence == 0.6
    assert claims[0].status == "SUPPORTED"


def test_generate_claim_from_documentation(tmp_path: Path):
    file_path = tmp_path / "README.md"
    file_path.write_text("# Knowledge Compiler\n")

    evidence = Evidence(
        source=file_path,
        kind="documentation",
        description="Repository documentation.",
    )

    claims = generate_claims([evidence])

    assert len(claims) == 1
    assert claims[0].statement == "The repository contains documentation."
    assert claims[0].evidence == (evidence,)
    assert claims[0].confidence == 0.6
    assert claims[0].status == "SUPPORTED"


def test_generate_claims_from_empty_evidence():
    assert generate_claims([]) == []


def test_generate_claims_ignores_unknown_evidence(tmp_path: Path):
    file_path = tmp_path / "something.bin"

    evidence = Evidence(
        source=file_path,
        kind="unknown",
        description="Unknown evidence.",
    )

    assert generate_claims([evidence]) == []

def test_generate_claim_for_repository_with_tests(tmp_path: Path):
    test_file = tmp_path / "test_payment.py"

    evidence = Evidence(
        source=test_file,
        kind="test",
        description="File contains 10 lines of source code.",
        language="Python"
    )

    claims = generate_claims([evidence])

    assert len(claims) == 1
    assert claims[0].statement == "The repository contains automated tests."
    assert claims[0].evidence == (evidence,)
    assert claims[0].status == "SUPPORTED"

def test_generate_claims_aggregates_evidence_for_same_statement(
    tmp_path: Path,
):
    first_file = tmp_path / "test_payment.py"
    second_file = tmp_path / "test_refund.py"

    first_evidence = Evidence(
        source=first_file,
        kind="test",
        description="Payment tests.",
        language="Python",
    )
    second_evidence = Evidence(
        source=second_file,
        kind="test",
        description="Refund tests.",
        language="Python",
    )

    claims = generate_claims([first_evidence, second_evidence])

    assert len(claims) == 1
    assert claims[0].statement == (
        "The repository contains automated tests."
    )
    assert claims[0].evidence == (first_evidence, second_evidence)
    assert claims[0].confidence == 0.8
    assert claims[0].status == "SUPPORTED"


def test_generate_claims_keeps_different_statements_separate(
    tmp_path: Path,
):
    documentation = Evidence(
        source=tmp_path / "README.md",
        kind="documentation",
        description="Repository documentation.",
    )
    tests = Evidence(
        source=tmp_path / "test_app.py",
        kind="test",
        description="Application tests.",
    )

    claims = generate_claims([documentation, tests])

    assert len(claims) == 2
    assert claims[0].statement == (
        "The repository contains documentation."
    )
    assert claims[1].statement == (
        "The repository contains automated tests."
    )

def test_generate_claims_from_ai_observation():
    evidence = [
        Evidence(
            source=Path("payments.py"),
            kind="ai_observation",
            description="The function returns True.",
            content="def process_payment():\n    return True",
            line_start=1,
            line_end=2,
        )
    ]

    claims = generate_claims(evidence)

    assert len(claims) == 1
    assert claims[0].statement == "The function returns True."
    assert claims[0].evidence == tuple(evidence)
    assert claims[0].evidence[0].line_start == 1
    assert claims[0].status == "UNKNOWN"


def test_generate_claims_aggregates_identical_ai_observations():
    evidence = [
        Evidence(
            source=Path("payments.py"),
            kind="ai_observation",
            description="The function returns True.",
        ),
        Evidence(
            source=Path("refunds.py"),
            kind="ai_observation",
            description="The function returns True.",
        ),
    ]

    claims = generate_claims(evidence)

    assert len(claims) == 1
    assert len(claims[0].evidence) == 2
    assert {item.source for item in claims[0].evidence} == {
        Path("payments.py"),
        Path("refunds.py"),
    }
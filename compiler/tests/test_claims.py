from pathlib import Path

from knowledge_compiler.claims import generate_claims
from knowledge_compiler.models import Evidence, ClaimStatus, Observation
from knowledge_compiler.observation_validation import (
    ObservationValidation,
    ValidationStatus,
)


def make_observation(
    statement: str,
    unit_id: str = "payments.py:function:1:2:process_payment",
) -> Observation:
    return Observation(
        unit_id=unit_id,
        statement=statement,
        source=Path("payments.py"),
        line_start=1,
        line_end=2,
    )


def test_generate_claim_from_file_content(tmp_path: Path):
    file_path = tmp_path / "example.py"

    evidence = Evidence(
        source=Path("example.py"),
        kind="file_content",
        description="File contains 1 lines of source code.",
    )

    claims = generate_claims([evidence])

    assert len(claims) == 1
    assert claims[0].statement == (
        "The repository contains source code in example.py."
    )
    assert claims[0].evidence == (evidence,)
    assert claims[0].confidence == 1.0
    assert claims[0].status == ClaimStatus.VERIFIED


def test_generate_claim_from_documentation(tmp_path: Path):
    file_path = tmp_path / "README.md"

    evidence = Evidence(
        source=file_path,
        kind="documentation",
        description="Repository documentation.",
    )

    claims = generate_claims([evidence])

    assert len(claims) == 1
    assert claims[0].statement == "The repository contains documentation."
    assert claims[0].evidence == (evidence,)
    assert claims[0].confidence == 1.0
    assert claims[0].status == ClaimStatus.VERIFIED


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
        language="Python",
    )

    claims = generate_claims([evidence])

    assert len(claims) == 1
    assert claims[0].statement == "The repository contains automated tests."
    assert claims[0].evidence == (evidence,)
    assert claims[0].status == ClaimStatus.VERIFIED


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

    claims = generate_claims(
        [first_evidence, second_evidence]
    )

    assert len(claims) == 1
    assert claims[0].statement == (
        "The repository contains automated tests."
    )
    assert claims[0].evidence == (
        first_evidence,
        second_evidence,
    )
    assert claims[0].confidence == 1.0
    assert claims[0].status == ClaimStatus.VERIFIED


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

    claims = generate_claims(
        [documentation, tests]
    )

    assert len(claims) == 2

    assert claims[0].statement == (
        "The repository contains documentation."
    )

    assert claims[1].statement == (
        "The repository contains automated tests."
    )


def test_ai_observation_alone_does_not_create_claim():
    evidence = [
        Evidence(
            source=Path("payments.py"),
            kind="ai_observation",
            description="The function returns True.",
            content="def process_payment():\n    return True",
            line_start=1,
            line_end=2,
            origin="ai",
        )
    ]

    claims = generate_claims(evidence)

    assert claims == []


def test_ai_observation_is_not_aggregated_as_evidence():
    evidence = [
        Evidence(
            source=Path("payments.py"),
            kind="ai_observation",
            description="The function returns True.",
            origin="ai",
        ),
        Evidence(
            source=Path("refunds.py"),
            kind="ai_observation",
            description="The function returns True.",
            origin="ai",
        ),
    ]

    claims = generate_claims(evidence)

    assert claims == []


def test_generate_claim_from_dependency(tmp_path: Path):
    file_path = tmp_path / "requirements.txt"

    evidence = Evidence(
        source=file_path,
        kind="dependency",
        description="Repository dependency declaration.",
    )

    claims = generate_claims([evidence])

    assert len(claims) == 1
    assert claims[0].statement == (
        "The repository declares dependencies in requirements.txt."
    )
    assert claims[0].evidence == (evidence,)
    assert claims[0].status == ClaimStatus.VERIFIED


def test_claims_status_includes_stale():
    assert ClaimStatus.STALE.value == "STALE"


def test_ai_observation_cannot_be_verified():
    observation = make_observation(
        "The function validates payments."
    )

    validation = ObservationValidation(
        unit_id=observation.unit_id,
        observation=observation,
        status=ValidationStatus.INCONCLUSIVE,
    )

    claims = generate_claims(
        [],
        validations=[validation],
    )

    assert len(claims) == 1
    assert claims[0].status == ClaimStatus.UNKNOWN
    assert claims[0].statement == (
        "The function validates payments."
    )


def test_ai_observation_supported_by_deterministic_evidence():
    observation = make_observation(
        "The function returns True."
    )

    deterministic_evidence = Evidence(
        source=Path("payments.py"),
        kind="function",
        description="Function 'process_payment' is defined.",
        origin="deterministic",
    )

    validation = ObservationValidation(
        unit_id=observation.unit_id,
        observation=observation,
        status=ValidationStatus.SUPPORTED,
        supporting_evidence=(deterministic_evidence,),
    )

    claims = generate_claims(
        [],
        validations=[validation],
    )

    assert len(claims) == 1
    assert claims[0].statement == (
        "The function returns True."
    )
    assert claims[0].status == ClaimStatus.SUPPORTED
    assert claims[0].evidence == (
        deterministic_evidence,
    )


def test_ai_observation_contradicted_by_deterministic_evidence():
    observation = make_observation(
        "The function returns True."
    )

    deterministic_evidence = Evidence(
        source=Path("payments.py"),
        kind="function",
        description="Function 'process_payment' returns False.",
        origin="deterministic",
    )

    validation = ObservationValidation(
        unit_id=observation.unit_id,
        observation=observation,
        status=ValidationStatus.CONTRADICTED,
        contradicting_evidence=(deterministic_evidence,),
    )

    claims = generate_claims(
        [],
        validations=[validation],
    )

    assert len(claims) == 1
    assert claims[0].statement == (
        "The function returns True."
    )
    assert claims[0].status == ClaimStatus.CONTRADICTED
    assert claims[0].evidence == (
        deterministic_evidence,
    )
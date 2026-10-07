from pathlib import Path

from knowledge_compiler.investigation import InvestigationUnit
from knowledge_compiler.investigator import InvestigationResult
from knowledge_compiler.models import Evidence, Observation
from knowledge_compiler.observation_validation import (
    ValidationStatus,
    validate_observations,
)


def make_result(
    observations: tuple[str, ...],
) -> InvestigationResult:
    unit = InvestigationUnit(
        source=Path("payments.py"),
        name="process_payment",
        kind="function",
        content="def process_payment():\n    pass\n",
        line_start=1,
        line_end=2,
    )

    return InvestigationResult(
        unit=unit,
        observations=tuple(
            Observation(
                unit_id=unit.unit_id,
                statement=observation,
                source=unit.source,
                line_start=unit.line_start,
                line_end=unit.line_end,
            )
            for observation in observations
        ),
    )


def test_observation_without_evidence_is_inconclusive():
    result = make_result(
        ("The function prevents duplicate payments.",)
    )

    validations = validate_observations(result, [])

    assert len(validations) == 1
    assert validations[0].status == ValidationStatus.INCONCLUSIVE


def test_ai_observation_cannot_validate_itself():
    result = make_result(
        ("The function prevents duplicate payments.",)
    )

    ai_evidence = Evidence(
        source=Path("payments.py"),
        kind="ai_observation",
        description="The function prevents duplicate payments.",
        content="def process_payment():\n    pass\n",
    )

    validations = validate_observations(result, [ai_evidence])

    assert validations[0].status == ValidationStatus.INCONCLUSIVE
    assert validations[0].supporting_evidence == ()
    assert validations[0].contradicting_evidence == ()


def test_unmatched_independent_evidence_is_inconclusive():
    result = make_result(
        ("The function prevents duplicate payments.",)
    )

    unrelated_evidence = Evidence(
        source=Path("README.md"),
        kind="documentation",
        description="The application uses Flask.",
    )

    validations = validate_observations(
        result,
        [unrelated_evidence],
    )

    assert validations[0].status == ValidationStatus.INCONCLUSIVE


def test_validation_result_preserves_observation():
    result = make_result(
        ("The function prevents duplicate payments.",)
    )

    validations = validate_observations(result, [])

    assert validations[0].observation.statement == (
        "The function prevents duplicate payments."
    )


def test_ai_evidence_is_not_independent():
    result = make_result(
        ("The function prevents duplicate payments.",)
    )

    ai_evidence = Evidence(
        source=Path("payments.py"),
        kind="ai_observation",
        description="The function prevents duplicate payments.",
    )

    validations = validate_observations(result, [ai_evidence])

    assert validations[0].status == ValidationStatus.INCONCLUSIVE


def test_linked_evidence_does_not_automatically_prove_claim():
    result = make_result(
        ("The function prevents duplicate payments.",)
    )

    source_evidence = Evidence(
        source=Path("payments.py"),
        kind="file_content",
        description="Source code for process_payment.",
        content="def process_payment():\n    pass\n",
    )

    validations = validate_observations(
        result,
        [source_evidence],
        evidence_links={
            "The function prevents duplicate payments.": [source_evidence]
        },
    )

    assert validations[0].status == ValidationStatus.INCONCLUSIVE


def test_unlinked_evidence_does_not_validate_observation():
    result = make_result(
        ("The project uses Flask.",)
    )

    documentation = Evidence(
        source=Path("README.md"),
        kind="documentation",
        description="The project uses Flask.",
    )

    validations = validate_observations(result, [documentation])

    assert validations[0].status == ValidationStatus.INCONCLUSIVE


def test_supported_observation_returns_supported():
    result = make_result(
        ("The function processes payments.",)
    )

    source_evidence = Evidence(
        source=Path("payments.py"),
        kind="file_content",
        description="Source code for process_payment.",
        content="""
def process_payment():
    process_transaction()
    return True
""",
    )

    def verifier(observations, source_content):
        assert observations == (
            "The function processes payments.",
        )
        return [ValidationStatus.SUPPORTED]

    validations = validate_observations(
        result,
        [source_evidence],
        verifier=verifier,
    )

    assert validations[0].status == ValidationStatus.SUPPORTED
    assert validations[0].supporting_evidence == (source_evidence,)
    assert validations[0].contradicting_evidence == ()


def test_contradicted_observation_returns_contradicted():
    result = make_result(
        ("The function prevents duplicate payments.",)
    )

    source_evidence = Evidence(
        source=Path("payments.py"),
        kind="file_content",
        description="Source code for process_payment.",
        content="""
def process_payment():
    create_payment()
    return True
""",
    )

    def verifier(observations, source_content):
        return [ValidationStatus.CONTRADICTED]

    validations = validate_observations(
        result,
        [source_evidence],
        verifier=verifier,
    )

    assert validations[0].status == ValidationStatus.CONTRADICTED
    assert validations[0].supporting_evidence == ()
    assert validations[0].contradicting_evidence == (source_evidence,)


def test_verifier_receives_observation_and_source():
    result = make_result(
        ("The function processes payments.",)
    )

    source_evidence = Evidence(
        source=Path("payments.py"),
        kind="file_content",
        description="Source code for process_payment.",
        content="def process_payment():\n    return True\n",
    )

    received = {}

    def verifier(observations, source_content):
        received["observation"] = observations
        received["source"] = source_content
        return [ValidationStatus.SUPPORTED]

    validate_observations(
        result,
        [source_evidence],
        verifier=verifier,
    )

    assert received["observation"] == (
        "The function processes payments.",
    )
    assert "def process_payment" in received["source"]


def test_validation_result_preserves_unit_id():
    result = make_result(
        ("The function prevents duplicate payments.",)
    )

    validations = validate_observations(result, [])

    assert validations[0].unit_id == result.unit.unit_id
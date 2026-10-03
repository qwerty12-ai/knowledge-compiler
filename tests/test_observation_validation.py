from pathlib import Path

from knowledge_compiler.investigator import InvestigationResult
from knowledge_compiler.models import Evidence
from knowledge_compiler.observation_validation import (
    ValidationStatus,
    validate_observations,
)
from knowledge_compiler.investigation import InvestigationUnit


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
        observations=observations,
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
    observation = "The function prevents duplicate payments."
    result = make_result((observation,))

    validations = validate_observations(result, [])

    assert validations[0].observation == observation

def test_ai_evidence_is_not_independent():
    result = make_result(("The function prevents duplicate payments.",))

    ai_evidence = Evidence(
        source=Path("payments.py"),
        kind="ai_observation",
        description="The function prevents duplicate payments.",
    )

    validations = validate_observations(result, [ai_evidence])

    assert validations[0].status == ValidationStatus.INCONCLUSIVE


def test_linked_evidence_does_not_automatically_prove_claim():
    result = make_result(("The function prevents duplicate payments.",))

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
    result = make_result(("The project uses Flask.",))

    documentation = Evidence(
        source=Path("README.md"),
        kind="documentation",
        description="The project uses Flask.",
    )

    validations = validate_observations(result, [documentation])

    assert validations[0].status == ValidationStatus.INCONCLUSIVE
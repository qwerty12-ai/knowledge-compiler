from pathlib import Path
from knowledge_compiler.models import Observation
from knowledge_compiler.investigation import InvestigationUnit
from knowledge_compiler.investigator import InvestigationResult
from knowledge_compiler.observation_evidence import (
    convert_observations_to_evidence,
)

def test_convert_observations_to_evidence():
    unit = InvestigationUnit(
        source=Path("payments.py"),
        name="process_payment",
        kind="function",
        content="def process_payment():\n    return True",
        line_start=1,
        line_end=2,
    )

    result = InvestigationResult(
        unit=unit,
        observations=(
            Observation(
                unit_id=unit.unit_id,
                statement="The function returns True.",
                source=unit.source,
                line_start=unit.line_start,
                line_end=unit.line_end
            )
        ,),
    )

    evidence = convert_observations_to_evidence(result)

    assert len(evidence) == 1
    assert evidence[0].source == Path("payments.py")
    assert evidence[0].kind == "ai_observation"
    assert evidence[0].description == "The function returns True."
    assert evidence[0].content == unit.content
    assert evidence[0].line_start == 1
    assert evidence[0].line_end == 2
    assert evidence[0].unit_id == result.unit.unit_id


def test_convert_empty_observations():
    unit = InvestigationUnit(
        source=Path("payments.py"),
        name="process_payment",
        kind="function",
        content="def process_payment():\n    return True",
    )

    result = InvestigationResult(unit=unit, observations=())

    assert convert_observations_to_evidence(result) == []
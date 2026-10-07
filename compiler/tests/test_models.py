import pytest
from pathlib import Path
from knowledge_compiler.models import Claim, Evidence, Observation

def test_claim_can_be_created():
    evidence = Evidence(
        source=Path("README.md"),
        kind="documentation",
        description="Project demonstration"
    )

    claim = Claim(
        statement="The repository contains project documentation.",
        evidence=(evidence,),
        confidence=0.95,
        status="SUPPORTED"
    )

    assert claim.statement == "The repository contains project documentation."
    assert claim.evidence == (evidence,)
    assert claim.confidence == 0.95
    assert claim.status == "SUPPORTED"

def test_claim_rejects_invalid_confidence():
    evidence = Evidence(
        source=Path("README.md"),
        kind="documentation",
        description="Project documentation",
    )

    with pytest.raises(ValueError):
        Claim(
            statement="The repository contains project documentation.",
            evidence=(evidence,),
            confidence=1.5,
            status="SUPPORTED",
        )


def test_claim_rejects_negative_confidence():
    evidence = Evidence(
        source=Path("README.md"),
        kind="documentation",
        description="Project documentation",
    )

    with pytest.raises(ValueError):
        Claim(
            statement="The repository contains project documentation.",
            evidence=(evidence,),
            confidence=-0.1,
            status="SUPPORTED",
        )

def test_observation_has_identity():
    observation = Observation(
        unit_id="payments.py:function:1:2:process_payment",
        statement="The function returns True.",
        source=Path("payments.py"),
        line_start=1,
        line_end=2
    )

    assert observation.unit_id == "payments.py:function:1:2:process_payment"
    assert observation.statement == "The function returns True."
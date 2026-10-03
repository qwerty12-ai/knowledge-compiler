import json
from pathlib import Path

from knowledge_compiler.models import Claim, Evidence
from knowledge_compiler.output import build_analysis_result


def test_analysis_result_serializes_to_json():
    source = Evidence(
        source=Path("README.md"),
        kind="documentation",
        description="Project documentation exists.",
    )

    claim = Claim(
        statement="The repository contains documentation.",
        evidence=(source,),
        confidence=0.6,
        status="SUPPORTED",
    )

    result = build_analysis_result(
        repository=Path("."),
        files_discovered=1,
        evidence=[source],
        claims=[claim],
    )

    payload = json.loads(result.to_json())

    assert payload["schema_version"] == "1.0"
    assert payload["files_discovered"] == 1
    assert payload["claims"][0]["statement"] == (
        "The repository contains documentation."
    )


def test_claim_references_its_evidence():
    source = Evidence(
        source=Path("README.md"),
        kind="documentation",
        description="Project documentation exists.",
    )

    claim = Claim(
        statement="The repository contains documentation.",
        evidence=(source,),
        confidence=0.6,
        status="SUPPORTED",
    )

    result = build_analysis_result(
        repository=Path("."),
        files_discovered=1,
        evidence=[source],
        claims=[claim],
    )

    assert result.claims[0].evidence_ids == ("evidence-0001",)
    assert result.claims[0].evidence_ids[0] == result.evidence[0].id


def test_empty_analysis_result():
    result = build_analysis_result(
        repository=Path("."),
        files_discovered=0,
        evidence=[],
        claims=[],
    )

    payload = json.loads(result.to_json())

    assert payload["claims"] == []
    assert payload["evidence"] == []
    assert payload["errors"] == []


def test_analysis_options_and_errors_are_preserved():
    result = build_analysis_result(
        repository=Path("."),
        files_discovered=3,
        evidence=[],
        claims=[],
        with_ai=True,
        limit=2,
        errors=["One file could not be read."],
    )

    payload = json.loads(result.to_json())

    assert payload["with_ai"] is True
    assert payload["limit"] == 2
    assert payload["errors"] == ["One file could not be read."]
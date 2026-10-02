from pathlib import Path

from knowledge_compiler.confidence import assess_confidence
from knowledge_compiler.models import Evidence


def make_evidence(source: str, kind: str = "file_content") -> Evidence:
    return Evidence(
        source=Path(source),
        kind=kind,
        description="Test evidence",
    )


def test_confidence_is_zero_without_evidence():
    assert assess_confidence(()) == 0.0


def test_confidence_is_point_six_for_one_source():
    evidence = (make_evidence("src/main.py"),)

    assert assess_confidence(evidence) == 0.6


def test_repeated_evidence_from_same_source_does_not_increase_confidence():
    evidence = (
        make_evidence("src/main.py", "file_content"),
        make_evidence("src/main.py", "test"),
    )

    assert assess_confidence(evidence) == 0.6


def test_multiple_sources_of_same_kind_have_point_eight_confidence():
    evidence = (
        make_evidence("src/main.py"),
        make_evidence("src/utils.py"),
    )

    assert assess_confidence(evidence) == 0.8


def test_multiple_sources_and_evidence_kinds_have_point_nine_confidence():
    evidence = (
        make_evidence("README.md", "documentation"),
        make_evidence("tests/test_main.py", "test"),
    )

    assert assess_confidence(evidence) == 0.9
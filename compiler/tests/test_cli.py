from knowledge_compiler.cli import analyze
from knowledge_compiler.investigator import InvestigationResult

def fake_investigate(unit):
    return InvestigationResult(
        unit=unit,
        observations=("The unit contains a test observation.",)
    )

def test_analyze_existing_repository(capsys, monkeypatch):
    monkeypatch.setattr(
        "knowledge_compiler.pipeline.investigate",
        fake_investigate
    )

    result = analyze(".")

    assert result is not None
    assert result.files_discovered > 0
    assert len(result.claims) > 0

def test_analyze_missing_repository(capsys):
    import pytest

    with pytest.raises(ValueError, match="repository does not exist"):
        analyze("./does-not-exist")
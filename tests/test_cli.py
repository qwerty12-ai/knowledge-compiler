from knowledge_compiler.cli import analyze
from knowledge_compiler.investigator import InvestigationResult

def fake_investigate(unit):
    return InvestigationResult(
        unit=unit,
        observations=("The unit contains a test observation.",)
    )

def test_analyze_existing_repository(capsys, monkeypatch):
    monkeypatch.setattr(
        "knowledge_compiler.cli.investigate",
        fake_investigate
    )

    analyze(".")

    captured = capsys.readouterr()

    assert "Analyzing repository:" in captured.out
    assert "Generated" in captured.out
    assert "Claim:" in captured.out

def test_analyze_missing_repository(capsys):
    analyze("./does-not-exist")

    captured = capsys.readouterr()
    
    assert "repository does not exist" in captured.out
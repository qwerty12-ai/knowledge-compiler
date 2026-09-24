from knowledge_compiler.cli import analyze

def test_analyze_existing_repository(capsys):
    analyze(".")

    captured = capsys.readouterr()

    assert "Analyzing repository:" in captured.out
    assert "Generated" in captured.out
    assert "Claim:" in captured.out

def test_analyze_missing_repository(capsys):
    analyze("./does-not-exist")

    captured = capsys.readouterr()
    
    assert "repository does not exist" in captured.out
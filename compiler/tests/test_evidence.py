from pathlib import Path

from knowledge_compiler.evidence import extract_evidence


def test_extract_evidence_from_text_file(tmp_path):
    file_path = tmp_path / "example.py"
    file_path.write_text("print('hello')\nprint('world')\n")

    evidence = extract_evidence(file_path, file_path.parent)

    assert len(evidence) == 1
    assert evidence[0].source == Path("example.py")
    assert evidence[0].kind == "file_content"
    assert "2 lines" in evidence[0].description


def test_extract_evidence_from_empty_file(tmp_path):
    file_path = tmp_path / "empty.py"
    file_path.write_text("")

    evidence = extract_evidence(file_path, file_path.parent)

    assert evidence == []


def test_extract_evidence_from_invalid_utf8(tmp_path):
    file_path = tmp_path / "binary.py"
    file_path.write_bytes(b"\xff\xfe\xfd")

    evidence = extract_evidence(file_path, file_path.parent)

    assert evidence == []

def test_extract_evidence_from_readme(tmp_path):
    file_path = tmp_path / "README.md"
    file_path.write_text("# Knowledge Compiler\n")

    evidence = extract_evidence(file_path, file_path.parent)

    assert len(evidence) == 1
    assert evidence[0].kind == "documentation"


def test_extract_evidence_from_dependency_file(tmp_path):
    file_path = tmp_path / "pyproject.toml"
    file_path.write_text("[project]\nname = 'demo'\n")

    evidence = extract_evidence(file_path, file_path.parent)

    assert len(evidence) == 1
    assert evidence[0].kind == "dependency"


def test_extract_evidence_from_test_file(tmp_path):
    file_path = tmp_path / "test_auth.py"
    file_path.write_text("def test_login():\n    assert True\n")

    evidence = extract_evidence(file_path, file_path.parent)

    assert len(evidence) == 1
    assert evidence[0].kind == "test"

def test_extract_evidence_includes_language(tmp_path):
    file_path = tmp_path / "test_auth.py"
    file_path.write_text("print('hello')\n")

    evidence = extract_evidence(file_path, file_path.parent)

    assert len(evidence) == 1
    assert evidence[0].language == "Python"

def test_extract_evidence_includes_content(tmp_path):
    file_path = tmp_path / "example.py"
    content = "def hello():\nreturn 'world'\n"
    file_path.write_text(content)

    evidence = extract_evidence(file_path, file_path.parent)

    assert len(evidence) == 1
    assert evidence[0].content == content

def test_extract_evidence_includes_line_ranges(tmp_path):
    file_path = tmp_path / "example.py"
    content = "def hello():\nreturn 'world'\n"
    file_path.write_text(content)
    
    evidence = extract_evidence(file_path, file_path.parent)
    
    assert len(evidence) == 1
    assert evidence[0].line_start == 1
    assert evidence[0].line_end == 2

def test_extract_evidence_uses_ast_compatible_line_count(tmp_path):
    file_path = tmp_path / "example.py"
    content = (
        "x = 1\n"
        "\x0c"
        "def hello():\n"
        "   return 'world'\n"
    )
    file_path.write_text(content)
    
    evidence = extract_evidence(file_path, file_path.parent)
    
    assert len(evidence) == 1
    assert evidence[0].line_start == 1
    assert evidence[0].line_end == 3
from pathlib import Path

from knowledge_compiler.discovery import discover_files


def test_discover_files_skips_ignored_directories(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / ".venv").mkdir()
    (tmp_path / "node_modules").mkdir()

    (tmp_path / "src" / "main.py").write_text("print('hello')")
    (tmp_path / ".venv" / "ignored.py").write_text("ignored")
    (tmp_path / "node_modules" / "ignored.js").write_text("ignored")

    files = discover_files(tmp_path)

    assert files == [Path(tmp_path / "src" / "main.py")]
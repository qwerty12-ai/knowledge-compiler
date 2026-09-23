from pathlib import Path
from knowledge_compiler.discovery import discover_files
from knowledge_compiler.models import DiscoveredFile


def test_discover_files_skips_ignored_directories(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / ".venv").mkdir()
    (tmp_path / "node_modules").mkdir()

    (tmp_path / "src" / "main.py").write_text("print('hello')")
    (tmp_path / ".venv" / "ignored.py").write_text("ignored")
    (tmp_path / "node_modules" / "ignored.js").write_text("ignored")

    files = discover_files(tmp_path)

    assert len(files) == 1
    assert files[0].path == Path("src/main.py")

def test_discover_files_skips_egg_info(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "project.egg-info").mkdir()

    (tmp_path / "src" / "main.py").write_text("print('hello')")
    (tmp_path / "project.egg-info" / "PKG-INFO").write_text("generated")

    files = discover_files(tmp_path)

    assert files == [
        DiscoveredFile(
            path=Path("src/main.py"),
            extension=".py",
            language="Python",
            size_bytes=len("print('hello')".encode()),
            category="source"
        )
    ]
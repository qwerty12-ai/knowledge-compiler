from pathlib import Path
from knowledge_compiler.models import Evidence
from knowledge_compiler.discovery import detect_language
from knowledge_compiler.source_lines import split_source_lines

def extract_evidence(file_path: Path, repository_root: Path) -> list[Evidence]:
    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    if not content.strip():
        return []

    name = file_path.name.lower()

    if name == "readme.md":
        kind = "documentation"
    elif name in {"pyproject.toml", "requirements.txt", "package.json"}:
        kind = "dependency"
    elif name.startswith("test_") or name.endswith("_test.py"):
        kind = "test"
    else:
        kind = "file_content"

    lines = split_source_lines(content)

    return [
        Evidence(
            source=file_path.relative_to(repository_root),
            kind=kind,
            description=f"File contains {len(lines)} lines of content.",
            language=detect_language(file_path),
            content=content,
            line_start=1,
            line_end=len(lines)
        )
    ]
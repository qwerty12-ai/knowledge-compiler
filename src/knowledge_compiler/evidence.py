from pathlib import Path
from knowledge_compiler.models import Evidence

def extract_evidence(file_path: Path) -> list[Evidence]:
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

    return [
        Evidence(
            source=file_path,
            kind=kind,
            description=f"File contains {len(content.splitlines())} lines of source code."
        )
    ]
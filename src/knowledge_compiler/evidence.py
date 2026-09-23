from pathlib import Path
from knowledge_compiler.models import Evidence

def extract_evidence(file_path: Path) -> list[Evidence]:
    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    if not content.strip():
        return []

    kind = "documentation" if file_path.name.lower() == "readme.md" else "file_content"

    return [
        Evidence(
            source=file_path,
            kind=kind,
            description=f"File contains {len(content.splitlines())} lines of source code."
        )
    ]
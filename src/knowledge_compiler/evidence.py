from pathlib import Path
from knowledge_compiler.models import Evidence

def extract_evidence(file_path: Path) -> list[Evidence]:
    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    if not content.strip():
        return []

    return [
        Evidence(
            source=file_path,
            kind="file_content",
            description=f"File contains {len(content.splitlines())} lines of source code."
        )
    ]
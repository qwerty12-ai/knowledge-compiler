from pathlib import Path
from knowledge_compiler.discovery import discover_files
from knowledge_compiler.evidence import extract_evidence
from knowledge_compiler.models import RepositoryContext

def build_repository_context(repository: Path) -> RepositoryContext:
    files = discover_files(repository)

    all_evidence = []

    for file in files:
        evidence = extract_evidence(repository / file.path)
        all_evidence.extend(evidence)

    return RepositoryContext(
        files=tuple(files),
        evidence=tuple(all_evidence)
    )
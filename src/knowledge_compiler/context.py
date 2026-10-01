from pathlib import Path
from knowledge_compiler.discovery import discover_files
from knowledge_compiler.evidence import extract_evidence
from knowledge_compiler.models import RepositoryContext
from knowledge_compiler.structure import extract_structure

def build_repository_context(repository: Path) -> RepositoryContext:
    files = discover_files(repository)

    all_evidence = []
    all_structures = []

    for file in files:
        file_path = repository / file.path

        evidence = extract_evidence(repository / file.path)
        all_evidence.extend(evidence)

        if file.language == "Python":
            try:
                structure = extract_structure(file_path)
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue

    all_structures.append(structure)

    return RepositoryContext(
        files=tuple(files),
        evidence=tuple(all_evidence),
        structures=tuple(all_structures)
    )
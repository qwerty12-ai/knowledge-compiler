from pathlib import Path
from knowledge_compiler.discovery import discover_files
from knowledge_compiler.evidence import extract_evidence
from knowledge_compiler.models import RepositoryContext
from knowledge_compiler.structure import extract_structure
from knowledge_compiler.models import Evidence, RepositoryContext

def build_repository_context(repository: Path) -> RepositoryContext:
    files = discover_files(repository)

    all_evidence = []
    all_structures = []

    for file in files:
        file_path = repository / file.path

        evidence = extract_evidence(repository / file.path, repository)
        all_evidence.extend(evidence)

        if file.language == "Python":
            try:
                structure = extract_structure(file_path, file.path)
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue

            all_structures.append(structure)

            for function in structure.functions:
                all_evidence.append(
                    Evidence(
                        source=function.source,
                        kind="function",
                        description=f"Function '{function.name}' is defined.",
                        language="Python",
                        line_start=function.line_start,
                        line_end=function.line_end,
                    )
                )

            for code_class in structure.classes:
                all_evidence.append(
                    Evidence(
                        source=code_class.source,
                        kind="class",
                        description=f"Class '{code_class.name}' is defined.",
                        language="Python",
                        line_start=code_class.line_start,
                        line_end=code_class.line_end,
                    )
                )

            for code_import in structure.imports:
                all_evidence.append(
                    Evidence(
                        source=code_import.source,
                        kind="import",
                        description=f"The file imports '{code_import.module}'.",
                        language="Python",
                        line_start=code_import.line,
                        line_end=code_import.line,
                    )
                )

    return RepositoryContext(
        files=tuple(files),
        evidence=tuple(all_evidence),
        structures=tuple(all_structures)
    )
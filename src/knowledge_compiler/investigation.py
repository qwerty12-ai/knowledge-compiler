from dataclasses import dataclass
from pathlib import Path
from knowledge_compiler.models import RepositoryContext

@dataclass(frozen=True)
class InvestigationUnit:
    source: Path
    name: str
    kind: str
    content: str
    line_start: int | None = None
    line_end: int | None = None

def build_investigation_units(context: RepositoryContext) -> list[InvestigationUnit]:
    units = []

    evidence_by_source = {
        item.source: item
        for item in context.evidence
        if item.content is not None
    }

    for evidence in context.evidence:
        if evidence.content is None:
            continue

        if evidence.kind == "documentation":
            units.append(InvestigationUnit(
                source=evidence.source,
                name=evidence.source.name,
                kind="documentation",
                content=evidence.content
            ))
        elif evidence.kind == "test":
            units.append(InvestigationUnit(
                source=evidence.source,
                name=evidence.source.name,
                kind="test",
                content=evidence.content
            ))

    for structure in context.structures:
        source = (
            structure.functions[0].source
            if structure.functions
            else structure.classes[0].source
            if structure.classes
            else None
        )

        if source is None:
            continue

        evidence = evidence_by_source.get(source)

        if evidence is None or evidence.content is None:
            continue

        lines = evidence.content.splitlines()

        for function in structure.functions:
            content = "\n".join(lines[function.line_start-1:function.line_end])

            units.append(InvestigationUnit(
                source=function.source,
                name=function.name,
                kind="function",
                content=content,
                line_start=function.line_start,
                line_end=function.line_end
            ))

        for code_class in structure.classes:
            content = "\n".join(lines[code_class.line_start-1:code_class.line_end])

            units.append(InvestigationUnit(
                source=code_class.source,
                name=code_class.name,
                kind="class",
                content=content,
                line_start=code_class.line_start,
                line_end=code_class.line_end
            ))

    return units
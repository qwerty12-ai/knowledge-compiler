from knowledge_compiler.structure import CodeStructure
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class DiscoveredFile:
    path: Path
    extension: str
    language: str | None
    size_bytes: int
    category: str

@dataclass(frozen=True)
class Evidence:
    source: Path
    kind: str
    description: str
    language: str | None = None
    content: str | None = None
    line_start: int | None = None
    line_end: int | None = None

@dataclass(frozen=True)
class Claim:
    statement: str
    evidence: tuple[Evidence, ...]
    confidence: float
    status: str

    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")

@dataclass(frozen=True)
class RepositoryContext:
    files: tuple[DiscoveredFile,...]
    evidence: tuple[Evidence,...]
    structures: tuple[CodeStructure,...] = ()
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class DiscoveredFile:
    path: Path
    extension: str
    language: str | None
    size_bytes: str
    category: str

@dataclass(frozen=True)
class Evidence:
    source: Path
    kind: str
    description: str
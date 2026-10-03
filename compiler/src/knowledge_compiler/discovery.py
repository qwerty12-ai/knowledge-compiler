from pathlib import Path
from .models import DiscoveredFile

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build"
}

LANGUAGE_BY_EXTENSION = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C/C++",
    ".hpp": "C++",
    ".md": "Markdown",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
}

def detect_language(path: Path) -> str | None:
    return LANGUAGE_BY_EXTENSION.get(path.suffix.lower())

def detect_category(path: Path) -> str:
    if path.name.startswith("test_") or path.name.endswith("_test.py"):
        return "test"

    if path.suffix.lower() in {".md", ".txt"}:
        return "documentation"

    if path.name in {"pyproject.toml", "package.json", "requirements.txt"}:
        return "configuration"

    return "source"

def discover_files(repository: Path) -> list[DiscoveredFile]:
    files = []

    for path in repository.rglob("*"):
        if not path.is_file():
            continue

        if any(part in IGNORED_DIRECTORIES or part.endswith(".egg-info") for part in path.parts):
            continue

        files.append(
            DiscoveredFile(
                path=path.relative_to(repository),
                extension=path.suffix.lower(),
                language=detect_language(path),
                size_bytes=path.stat().st_size,
                category=detect_category(path)
            )
        )

    return sorted(files, key=lambda file: str(file.path))
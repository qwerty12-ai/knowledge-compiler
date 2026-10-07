# Knowledge Compiler

The core analysis engine of the Knowledge Compiler project.

It analyzes software repositories and compiles structured, evidence-backed knowledge about the codebase.

## What It Does

The compiler analyzes:

- Source files
- Project structure
- Documentation
- Tests
- Dependencies
- AI-generated observations

It validates AI-generated observations against independent repository evidence and produces claims with confidence and status.

> Don't tell me what you think. Show me why you think it.

## Pipeline

```text
Repository
    ↓
Discovery
    ↓
Evidence
    ↓
Structure
    ↓
Investigation
    ↓
Observations
    ↓
Validation
    ↓
Claims
    ↓
Confidence / Status
```

AI is optional. Deterministic repository evidence remains the source of truth, while AI is used for semantic investigation and observation generation.

## Development

Install the compiler in editable mode with development dependencies:

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

Run the CLI:

```bash
knowledge-compiler analyze <repository>
```

Run AI-assisted analysis:

```bash
knowledge-compiler analyze <repository> --with-ai
```

## Status

The compiler is the core engine of the larger Knowledge Compiler application.

Detailed compiler architecture, pipeline, data model, CLI, and development documentation will be added as the project is finalized.
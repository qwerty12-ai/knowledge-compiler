# Knowledge Compiler — Compiler Architecture

The Knowledge Compiler is the core analysis engine behind the Knowledge Compiler project.

It inspects a software repository, extracts evidence, optionally investigates selected parts of the codebase using a local language model, validates AI-generated observations against independently extracted evidence, and produces structured engineering claims.

Its purpose is not to generate explanations that merely sound convincing. It is to make repository-derived knowledge traceable to the sources that support or contradict it.

## Core Principle

Every claim should be evaluated according to the evidence available for it.

The compiler distinguishes between:

- Deterministic findings established by implemented repository checks.
- Findings supported by extracted repository evidence.
- AI-generated observations that have undergone evidence-based validation.
- Claims that remain unknown or conflict with available evidence.

The compiler does not treat language-model output as ground truth.

---

## Architecture Overview

```text
Repository Path
      |
      v
Path Validation
      |
      v
Repository Context Builder
      |
      +--------------------------+
      |                          |
      v                          v
File Discovery             Evidence Extraction
      |                          |
      +-------------+------------+
                    |
                    v
             Repository Context
                    |
                    v
          Optional AI Investigation
                    |
                    v
          Observation Validation
                    |
                    v
             Claim Generation
                    |
                    v
             Analysis Result
                    |
          +---------+---------+
          |                   |
          v                   v
      Human CLI           JSON Output
```

The AI investigation stage is optional. The deterministic pipeline can produce an analysis without a language model.

## Pipeline Stages

### 1. Repository validation

The pipeline receives a repository path and validates that it points to an existing directory.

Invalid paths are rejected before repository analysis begins. A `--limit` below 1 is rejected at the same point.

### 2. File discovery

The discovery stage walks the repository recursively and collects every regular file that is not excluded (see below). It does not filter by extension: files with unrecognized extensions are discovered too, without a language label. `files_discovered` counts all of them.

The current implementation labels these extensions:

| Language or format | Extensions or filenames |
| ------------------ | ----------------------- |
| Python             | .py                     |
| JavaScript         | .js, .jsx               |
| TypeScript         | .ts, .tsx               |
| Java               | .java                   |
| Go                 | .go                     |
| Rust               | .rs                     |
| C                  | .c                      |
| C/C++ (headers)    | .h                      |
| C++                | .cpp, .hpp              |
| Markdown           | .md                     |
| JSON               | .json                   |
| YAML               | .yaml, .yml             |
| TOML               | .toml                   |

Each discovered file is also assigned a category: `test` (name starts with `test_` or ends with `_test.py`), `documentation` (`.md` or `.txt`), `configuration` (`pyproject.toml`, `package.json`, `requirements.txt`), or `source` (everything else).

Language recognition during discovery does not mean every language has a dedicated structural parser. The current AST-based structural extraction is primarily implemented for Python.

#### Excluded directories

Discovery skips common generated, cached, dependency, and version-control directories, including:

- `.git`
- `.venv`
- `venv`
- `__pycache__`
- `.pytest_cache`
- `.mypy_cache`
- `.ruff_cache`
- `node_modules`
- `.next`
- `out`
- `coverage`
- `dist`
- `build`

Directories ending in `.egg-info` are also excluded.

Symbolic links are skipped, and files larger than 1,000,000 bytes are excluded by the current implementation.

Directory names are matched against every component of the path discovery walks, including the parent directories of the repository when an absolute path is given. A repository stored under a directory with one of these names (for example `build` or `out`) may therefore be discovered as empty.

These rules reduce noise and avoid unnecessary work. They are not a complete security boundary for analyzing untrusted repositories.

### 3. Evidence extraction

The evidence extractor reads each discovered file as UTF-8 text.

Files that cannot be decoded or read are skipped, but still count toward `files_discovered`. Blank files do not produce content evidence. A whole-file evidence record spans line 1 to the last line and has the description `File contains N lines of content.`

Evidence records capture information such as:

- Source path
- Evidence kind
- Description
- Programming language, when identified
- Line numbers, when available
- Extracted content

The current implementation recognizes several evidence categories:

| Evidence kind | Source                                                                  |
| ------------- | ----------------------------------------------------------------------- |
| documentation | A file named `README.md`                                                |
| dependency    | `pyproject.toml`, `requirements.txt`, `package.json`                    |
| test          | A file whose name starts with `test_` or ends with `_test.py`           |
| file_content  | Every other readable, non-blank file (including Markdown, JSON, YAML)   |
| function      | Python AST: a function or method definition (line range, no content)    |
| class         | Python AST: a class definition (line range, no content)                 |
| import        | Python AST: an import statement (line, no content)                      |
| ai_observation| An AI-generated observation (added only when AI investigation is on)   |

Python source files receive additional structural extraction using the Python AST.

The structural extractor identifies constructs such as:

- Functions
- Classes
- Imports

This structural representation gives later stages more targeted units to investigate than undifferentiated source text alone. Python files that fail to parse (for example because of a syntax error) are skipped for structural extraction without an error being recorded.

**Important:** The current structural extraction does not provide equivalent AST analysis for every language recognized during file discovery.

### 4. Repository context construction

The context builder combines the discovered files, extracted evidence, and structural information into a `RepositoryContext`.

This context is the shared input for the later analysis stages.

Keeping repository discovery and evidence extraction separate from claim generation makes it possible to extend the compiler without tying every new capability to a single large function.

### 5. Optional AI investigation

When AI investigation is enabled, the compiler selects units from the repository context.

The compiler builds candidate units from `README.md` documentation, test files, Python functions, and Python classes. Before investigation the pipeline keeps only documentation, function, and class units, so test units are filtered out. Units are processed in the order they were built: documentation units first, then, for each Python file in path order, its functions followed by its classes.

The configured local model is `qwen3:4b` (`AI_MODEL` in `compiler/src/knowledge_compiler/config.py`, not configurable from the CLI), accessed through Ollama. The compiler creates the Ollama client with its default settings and does not set a host itself.

The model is asked, with one call per unit, to return observations as JSON that are grounded in the supplied repository material. If the reply is not valid JSON in the expected shape, that unit yields no observations. If the call itself fails, the error is recorded in the result's `errors` and the pipeline continues with the next unit.

AI investigation is intentionally optional because:

- Deterministic analysis should remain useful without a language model.
- Local model latency depends on hardware and model configuration.
- AI output can be incorrect even when it sounds convincing.
- Not every repository needs AI investigation to establish basic structural facts.

#### The `--limit` option

`--limit N` limits the number of units considered for AI investigation. The pipeline applies it after filtering, by keeping the first N units in the order described above.

- It does not limit repository discovery, evidence extraction, or deterministic claim generation. `files_discovered` is unaffected.
- Deterministic analysis does not require AI and is not affected by `--limit`.
- `N` must be an integer of at least 1. Smaller values are rejected (`--limit must be at least 1`), with or without `--with-ai`.
- It is applied only inside the AI investigation path. If `--limit` is supplied without `--with-ai`, the CLI accepts the command and runs the deterministic analysis; the limit is not applied to anything. The supplied value is still recorded in the result's `limit` field next to `with_ai: false`.
- The CLI does not currently reject or warn about `--limit` without `--with-ai`, and no compiler test currently exercises `--limit` through the CLI.
- The web interface enables its limit field only when AI investigation is enabled (pre-filled with 100) and submits no limit when it is off. The API accepts a `limit` with or without `with_ai`; the pipeline ignores it unless AI investigation is enabled.
- A given N does not guarantee that the selected units cover the repository's important behavior.

#### AI investigation performance

In CPU-only testing, one AI investigation unit has taken roughly **2–3 minutes**. This is an observed estimate on one setup, not a benchmark or a guaranteed duration.

For illustration, 100 units processed sequentially at that rate would take about 200–300 minutes (roughly 3 hours 20 minutes to 5 hours), before accounting for overhead and differences in model behavior.

A capable GPU can substantially reduce inference time, depending on the GPU, available memory, model, and runtime configuration. No particular speedup is guaranteed. The same considerations apply whether AI investigation is started from the CLI or from the web application, whose limit field is pre-filled with 100.

Use `--limit` to bound the amount of AI work on CPU-only machines. The deterministic pipeline does not require a GPU.

### 6. Observation validation

Each unit's observations are checked against the independently extracted evidence from the same source file. Evidence of kind `ai_observation` is excluded, so the model's own assertion is never treated as confirmation of itself.

The check is a second call to the same local model (temperature 0), which classifies every observation as:

- `SUPPORTED`
- `CONTRADICTED`
- `INCONCLUSIVE`

Because the checker is a language model, the check can be wrong in either direction. It is evidence-based, not formal verification.

A result is `INCONCLUSIVE` when there is no independent evidence for the source file, when the model's reply is not valid JSON of the expected shape or has the wrong number of results, or when the verification call fails. Failures of the verification call are not recorded in `errors`.

The evidence attached to a `SUPPORTED` or `CONTRADICTED` observation is all independent evidence extracted from that source file. It is not a citation of specific lines.

When validation cannot establish a result, the compiler preserves that uncertainty rather than inventing supporting evidence.

### 7. Claim generation

The claim generator groups deterministic evidence into baseline claims, then adds one claim per validated AI observation.

Baseline claims are `VERIFIED` with confidence `1.0`, grouped by statement:

| Statement                                                   | Built from                                                              |
| ----------------------------------------------------------- | ----------------------------------------------------------------------- |
| The repository contains documentation.                      | All `documentation` evidence (one claim)                                |
| The repository contains source code in `<path>`.            | Each `file_content` file (one claim per file)                           |
| The repository contains automated tests.                    | All `test` evidence (one claim)                                         |
| The repository declares dependencies in `<file name>`.      | `dependency` evidence, grouped by file name                             |

The "source code" wording is used for every `file_content` file, including Markdown, JSON, and YAML files. Function, class, and import evidence does not generate claims.

`VERIFIED` means the repository check established the claim under the current implementation. It does not mean the compiler has formally proved every possible interpretation of the statement.

Validated AI observations are mapped to claim statuses as follows:

| Validation result | Claim status | Evidence behavior                                                              |
| ----------------- | ------------ | ------------------------------------------------------------------------------ |
| SUPPORTED         | SUPPORTED    | Supporting evidence is attached.                                               |
| CONTRADICTED      | CONTRADICTED | Contradicting evidence is attached.                                            |
| INCONCLUSIVE      | UNKNOWN      | The claim is retained without supporting evidence from that validation result. |

The current pipeline does not assign every status defined by the broader knowledge model. In particular, `WEAKLY_SUPPORTED` and `STALE` are not currently assigned by this claim-generation path.

## Claim and Evidence Model

A claim represents a statement about the repository. Evidence records represent the source material associated with an analysis.

A simplified claim looks like this:

```json
{
  "id": "claim-0001",
  "statement": "The repository contains automated tests.",
  "status": "VERIFIED",
  "confidence": 1.0,
  "evidence_ids": [
    "evidence-0001"
  ]
}
```

A simplified evidence record looks like this:

```json
{
  "id": "evidence-0001",
  "source": "compiler/tests/test_cli.py",
  "kind": "test",
  "description": "File contains 244 lines of content.",
  "origin": "deterministic",
  "language": "Python",
  "line_start": 1,
  "line_end": 244,
  "content": "..."
}
```

These examples illustrate the output structure; IDs, counts, and contents depend on the analysis. `origin` is `deterministic` for evidence extracted from the repository and `ai` for evidence created from an AI observation. An AI observation becomes an evidence record of kind `ai_observation` whose description is the observation text; it is not used to generate claims directly.

A structured record alone does not guarantee that a claim is true. The quality of the result depends on the extraction rules, the validation logic, the available source material, and the correctness of the relationship between claims and evidence.

### Claim statuses

| Status           | Meaning                                                           |
| ---------------- | ----------------------------------------------------------------- |
| VERIFIED         | Established by a deterministic check implemented by the compiler. |
| SUPPORTED        | Supported by available evidence.                                  |
| WEAKLY_SUPPORTED | Supported only weakly or incompletely.                            |
| UNKNOWN          | Not established by available evidence.                            |
| CONTRADICTED     | Conflicts with available evidence.                                |
| STALE            | May no longer reflect the current repository state.               |

### Evidence references

Claims refer to evidence using evidence IDs.

In compiler JSON output, IDs such as `claim-0001` and `evidence-0001` are local to the analysis result. They should not be interpreted as globally persistent identifiers.

The full evidence content can be included in ordinary JSON output. Compact JSON omits the content by setting the evidence `content` field to `null`.

## Confidence Scoring

The current confidence calculation is a heuristic. It considers the availability of evidence, source diversity, evidence kinds, and whether the claim is contradicted.

The implementation currently follows these general rules:

| Condition                                        | Base score |
| ------------------------------------------------ | ---------- |
| No evidence, or only ai_observation evidence     | 0.0        |
| Evidence from one unique source                  | 0.6        |
| Multiple sources with only one evidence kind     | 0.8        |
| Multiple sources and more than one evidence kind | 0.9        |

For contradicted claims, the implementation inverts the resulting score. `VERIFIED` baseline claims do not use this calculation; they are assigned `1.0` directly. In the current pipeline the evidence attached to an AI-derived claim comes from a single source file, so by these rules a `SUPPORTED` claim scores 0.6, a `CONTRADICTED` claim 0.4, and an `UNKNOWN` claim 0.0.

These scores are not calibrated probabilities. For example, a confidence score of `0.9` does not mean that the claim has a measured 90% chance of being true.

The scoring rules may evolve as the evidence model becomes more sophisticated.

## Analysis Result

The compiler returns an `AnalysisResult` containing the analysis metadata, claims, evidence, and errors.

The result includes fields such as:

| Field            | Description                               |
| ---------------- | ----------------------------------------- |
| schema_version   | Version of the result schema.             |
| repository       | Absolute path of the analyzed repository. |
| files_discovered | Number of discovered files (all non-excluded files up to the size limit). |
| with_ai          | Whether AI investigation was requested.   |
| limit            | The `--limit` value as supplied, or null. Recorded even when AI investigation is disabled. |
| claims           | Generated claims.                         |
| evidence         | Extracted evidence records.               |
| errors           | Errors recorded during processing.        |

The current schema version is `1.0`.

Treat this schema as an evolving interface. Consumers should not assume that fields or behavior will remain unchanged across future schema versions unless compatibility is explicitly documented.

## CLI Usage

Install the compiler from the repository root. CairoSVG, which the compiler imports for its terminal banner, needs the Cairo system library (`libcairo2` on Debian, Ubuntu, and WSL):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e "./compiler[dev]"
```

Analyze the current repository:

```bash
knowledge-compiler analyze .
```

Analyze a different repository:

```bash
knowledge-compiler analyze /path/to/repository
```

Enable AI investigation:

```bash
knowledge-compiler analyze /path/to/repository --with-ai
```

Limit AI investigation units (see [The `--limit` option](#the---limit-option)):

```bash
knowledge-compiler analyze /path/to/repository --with-ai --limit 10
```

Produce JSON output:

```bash
knowledge-compiler analyze /path/to/repository --json
```

Produce compact JSON:

```bash
knowledge-compiler analyze /path/to/repository --compact-json
```

Write JSON output to a file:

```bash
knowledge-compiler analyze /path/to/repository --json --output analysis.json
```

The `--json` and `--compact-json` options are intended for machine-readable output and are mutually exclusive. `--output` always writes JSON to the file (compact with `--compact-json`, full otherwise), whether or not `--json` is given. Consult `knowledge-compiler analyze --help` for the options available in the installed version.

### Compact output

Compact JSON preserves the evidence record structure while omitting full evidence content. This is useful when consumers need identifiers, metadata, and claim relationships without embedding every extracted source fragment.

### Running without AI

The deterministic workflow does not require a running Ollama service. When `--with-ai` is omitted, the compiler still discovers files, extracts evidence, and generates deterministic claims. This is the right default for CPU-only machines, quick first inspections, and environments without a local model. Passing `--limit` without `--with-ai` does not change this: the analysis is deterministic and the limit is not applied.

## Extending the Compiler

New compiler capabilities should preserve the separation between discovery, evidence extraction, investigation, validation, and claim generation.

When adding a feature:

- Identify the repository information the feature needs.
- Determine whether that information belongs in discovery, extraction, or a later stage.
- Keep extracted source evidence distinct from AI-generated observations.
- Add validation when a new claim depends on inferred behavior.
- Preserve uncertainty when evidence is insufficient.
- Add tests for both expected results and failure cases.
- Update the result schema documentation if the output contract changes.

Avoid making AI-generated text the sole evidence for a claim that is presented as verified.

### Adding language support

Recognizing a file extension is not the same as understanding the language.

Meaningful language support may require dedicated parsing, source locations, symbol extraction, and tests. Until those capabilities exist, document the distinction between file discovery and structural understanding.

### Adding claim types

A new claim type should define:

- What the claim asserts.
- Which evidence can support it.
- Which evidence can contradict it.
- When it should remain unknown.
- How its status and confidence are determined.
- How a user can trace it back to its sources.

## Testing

Run the compiler tests from the repository root:

```bash
python -m pytest compiler/tests/ -q
```

The compiler tests should cover:

- Repository path validation.
- File discovery and exclusions.
- Evidence extraction.
- Python structural extraction.
- AI-disabled analysis.
- AI observation validation.
- Claim generation and status mapping.
- Confidence scoring.
- JSON serialization.
- CLI argument handling and error paths.

When changing a stage, add or update tests at the narrowest useful level and run the complete compiler test suite before considering the change finished.

## Design Constraints

The compiler is designed around a few important constraints:

- **Evidence before explanation.** Claims should remain traceable to source material.
- **Deterministic baseline.** Basic repository analysis must not require a language model.
- **Optional AI.** Model investigation should enhance the workflow without becoming a prerequisite for using the compiler.
- **Explicit uncertainty.** An inconclusive result is better than an unsupported assertion presented as fact.
- **Modular pipeline.** Discovery, extraction, validation, and claim generation should remain understandable and independently testable.
- **Honest capability boundaries.** File recognition, structural parsing, semantic understanding, and formal verification are different capabilities and should not be conflated.

## Limitations and Security

- Structural extraction is primarily implemented for Python; discovery labels more languages than the structural analysis supports.
- Deterministic claims cover a limited set of repository properties.
- AI investigation covers `README.md` documentation, Python functions, and Python classes, and only the first N units when `--limit` is set.
- The validator is the same local model, so it can miss context or misread evidence, and its attached evidence is file-level.
- Directory exclusions and the file-size limit are not a sandbox.

Treat analyzed repositories as untrusted input. Do not execute repository code merely because it has been analyzed, do not pass secrets to a local model, and use appropriate isolation for repositories you do not trust.

## Further Reading

- [Project README](../README.md)
- [Development Guide](../docs/DEVELOPMENT.md)
- [Why I Built This](../docs/WHY_I_BUILT_THIS.md)
- [License](../LICENSE)
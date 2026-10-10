# Knowledge Compiler

**Show me what this codebase knows about itself.**

Knowledge Compiler analyzes a software repository and turns its implementation into structured, evidence-backed engineering knowledge.

Instead of asking an engineer to manually search through source files, tests, configuration, and documentation to understand an unfamiliar codebase, Knowledge Compiler builds a structured view of what the repository reveals about itself.

Its goal is simple:

> Don't tell me what you think. Show me why you think it.

---

## The Problem

Understanding an unfamiliar codebase is expensive.

The documentation might be outdated. A README might describe a feature that no longer exists. Configuration reveals only part of the system. Tests encode behavior that documentation never mentions. Important assumptions are scattered across functions, dependencies, and implementation details.

An engineer entering an unfamiliar production codebase must piece these clues together before they can confidently change anything.

This process can take days or weeks.

Knowledge Compiler is an attempt to make that investigation faster, more structured, and more transparent.

## What It Does

Knowledge Compiler inspects a repository, extracts evidence, generates engineering claims, and records the relationship between those claims and their supporting evidence.

Its current workflow is:

1. **Discover** — identify relevant files in a repository.
2. **Extract evidence** — collect source content and structural information.
3. **Investigate** — optionally use a local language model to investigate selected parts of the codebase.
4. **Validate** — check each AI-generated observation against independently extracted repository evidence. The check is performed by the local model.
5. **Generate claims** — represent findings as structured claims with statuses, confidence scores, and evidence references.
6. **Inspect** — explore analyses, claims, evidence, and processing state through the web interface (the forensic workstation).

The deterministic analysis works without a language model. AI investigation is optional.

## Current Capabilities

- Recursive repository discovery with exclusions for common generated and dependency directories.
- File-content extraction and Python AST-based discovery of functions, classes, and imports.
- Repository analysis through a Python CLI.
- Optional local AI investigation using Ollama.
- Validation of AI-generated observations against repository evidence.
- Structured claims with statuses and evidence references.
- JSON output for downstream processing.
- A FastAPI backend for creating and retrieving analyses.
- Background analysis jobs using Redis and BullMQ.
- MySQL persistence for analyses, claims, evidence, and claim-evidence relationships.
- A Next.js web interface for exploring analysis results.
- Server-sent events for analysis progress updates.
- A Redis Inspector for examining analysis state and related queue information.
- Automated tests and a GitHub Actions CI workflow.

These capabilities describe the current implementation, not a claim that every possible programming language or repository structure is fully understood.

## Architecture

```text
KNOWLEDGE COMPILER

Standalone CLI
     |
     v
Python Compiler
     |
     +--> Repository discovery
     |
     +--> Evidence extraction
     |
     +--> Optional AI investigation
     |
     +--> Observation validation
     |
     +--> Claim generation
     |
     +--> Structured JSON output

Web Application
     |
     v
Next.js Frontend
     |
     v
FastAPI Backend
     |
     +--> Redis / BullMQ
     |        |
     |        v
     |     Background Worker
     |        |
     |        v
     |     Python Compiler
     |        |
     |        v
     +------ MySQL
```

The standalone CLI and the web application are two ways to use the compiler. CLI output is produced directly by the compiler; it does not automatically appear in the web application's analysis history.

### Technology Stack

| Component                 | Technology                            |
| ------------------------- | ------------------------------------- |
| Compiler                  | Python 3.14+                          |
| CLI                       | Python package entry point            |
| Structural analysis       | Python AST                            |
| Optional AI investigation | Ollama                                |
| Local AI model            | qwen3:4b                              |
| Backend API               | FastAPI                               |
| Background jobs           | Redis and BullMQ                      |
| Persistence               | MySQL                                 |
| Frontend                  | Next.js, React, TypeScript            |
| Local infrastructure      | Docker Compose                        |
| CI                        | GitHub Actions                        |
| Testing                   | pytest and frontend lint/build checks |

The project uses local infrastructure for development. Production hosting and deployment decisions are documented separately as the application evolves.

## Knowledge Model

Knowledge Compiler separates a claim from the evidence used to support it.

A claim is a statement about the repository.

Evidence is an extracted source that helps establish whether the statement is justified.

For example:

```text
Claim:
The repository contains automated tests.

Status:
VERIFIED

Evidence:
compiler/tests/test_cli.py
compiler/tests/test_claims.py
```

The example illustrates the model; actual results depend on the repository being analyzed.

### Claim statuses

| Status           | Meaning                                                                                          |
| ---------------- | ------------------------------------------------------------------------------------------------ |
| VERIFIED         | A deterministic repository check establishes the claim under the current implementation's rules. |
| SUPPORTED        | Available evidence supports the claim, but it is not treated as deterministically verified.      |
| WEAKLY_SUPPORTED | Evidence provides limited support, but important uncertainty remains.                            |
| UNKNOWN          | Available evidence is insufficient to establish the claim.                                       |
| CONTRADICTED     | Available evidence conflicts with the claim.                                                     |
| STALE            | A previously established claim may no longer reflect the current repository state.               |

Not every status is assigned by every part of the current pipeline. In particular, `WEAKLY_SUPPORTED` and `STALE` are part of the knowledge model but are not currently assigned by the main claim-generation path.

### Confidence is not probability

The current confidence score is a heuristic based on evidence availability, source diversity, and claim status. It is not a statistically calibrated probability that a claim is true.

A high score should not be interpreted as mathematical proof.

### Evidence traceability

Claims reference evidence through evidence IDs. Evidence records can include:

- Source path
- Evidence kind
- Description
- Programming language, when identified
- Start and end line numbers, when available
- Extracted content
- Origin (`deterministic` or `ai`), in the compiler's JSON output

The web application's database stores the same fields except `origin`; AI-derived evidence remains identifiable by its `ai_observation` kind.

The JSON output uses analysis-local IDs such as `claim-0001` and `evidence-0001`. These are identifiers within an analysis result, not permanent database identifiers.

The objective is to make it possible to inspect why a claim was generated instead of presenting an unsupported conclusion.

## Quick Start: Standalone Compiler

### Requirements

- Python 3.14 or newer
- The Cairo system library (`libcairo2` on Debian, Ubuntu, and WSL). The compiler imports CairoSVG for its terminal banner, and CairoSVG depends on it. The backend Docker image installs `libcairo2`.
- Git, if you want to clone the repository

Clone the repository and enter its directory:

```bash
git clone https://github.com/qwerty12-ai/knowledge-compiler.git
cd knowledge-compiler
```

Install the compiler in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e "./compiler[dev]"
```

On Windows, activate the virtual environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Run an analysis:

```bash
knowledge-compiler analyze .
```

Analyze another repository:

```bash
knowledge-compiler analyze /path/to/repository
```

The CLI prints the analysis results to the terminal.

### JSON output

Generate JSON output:

```bash
knowledge-compiler analyze /path/to/repository --json
```

`--json` and `--compact-json` are mutually exclusive. Use compact JSON when you want a smaller machine-readable result:

```bash
knowledge-compiler analyze /path/to/repository --compact-json
```

Write output to a file:

```bash
knowledge-compiler analyze /path/to/repository --json --output analysis.json
```

`--output` always writes JSON to the file (compact when combined with `--compact-json`, full otherwise), whether or not `--json` is given. The terminal then prints only a confirmation line.

Limit the number of units considered by optional AI investigation:

```bash
knowledge-compiler analyze /path/to/repository --with-ai --limit 10
```

### The `--limit` option

`--limit N` limits the number of units considered for AI investigation.

- It does **not** limit the number of files discovered, the evidence extracted, or the deterministic claims generated.
- Deterministic analysis does not require AI, and `--limit` plays no part in it.
- `N` must be an integer of at least 1. Smaller values are rejected, with or without `--with-ai`.
- It is applied only inside the AI investigation path. If you pass `--limit` without `--with-ai`, the CLI accepts the command and runs the deterministic analysis; the limit is not applied to anything. The value you supplied is still recorded in the result's `limit` field. The CLI does not currently reject or warn about this combination.
- Units are taken in the order the compiler builds them: README documentation first, then the Python functions and classes of each file in path order. They are not ranked by importance.
- The web interface enables its limit field only when AI investigation is switched on, and submits no limit when it is off.

Check the CLI help for the exact options available in your installed version:

```bash
knowledge-compiler analyze --help
```

## Optional AI Investigation

AI investigation is optional. The deterministic baseline can run without Ollama.

To enable local AI investigation, install and start Ollama separately, then pull the configured model:

```bash
ollama pull qwen3:4b
```

Run an analysis with AI enabled:

```bash
knowledge-compiler analyze /path/to/repository --with-ai
```

The compiler uses the local model to generate observations about selected repository units. AI investigation considers `README.md` documentation, Python functions, and Python classes; test files are not investigated. Each observation is then checked against the independently extracted evidence from the same source file. That check is a second call to the same local model, so it can also be wrong.

The model name (`qwen3:4b`) is set in `compiler/src/knowledge_compiler/config.py` and cannot be changed from the CLI. The compiler uses the Ollama client's default connection settings and does not set a host itself.

This is not formal verification. A language model can misunderstand code, miss relevant context, or produce an incorrect observation. The validation stage is designed to avoid treating an AI-generated statement as established fact merely because the model produced it.

If investigating a unit fails (for example because Ollama is not reachable), the error is recorded in the result's `errors` and the compiler continues with the remaining units and the deterministic claims.

### CPU and GPU considerations

The deterministic analysis does not require a GPU.

AI investigation runs locally through Ollama, so its performance depends on the selected model, available memory, CPU, GPU, and other hardware characteristics.

In CPU-only testing, one AI investigation unit has taken roughly **2–3 minutes**. This is an observed estimate on one setup, not a benchmark or a guaranteed duration. As an illustration, 100 units processed sequentially at that rate would take about 200–300 minutes (roughly 3 hours 20 minutes to 5 hours), before accounting for overhead and differences in model behavior.

A capable GPU can substantially reduce model inference latency, but the speedup depends on the GPU, available memory, model, and runtime configuration; no particular speedup is guaranteed. A GPU is not a requirement for using the core compiler. Use `--limit` to bound how much work AI investigation does on CPU-only machines. The web interface pre-fills its limit field with 100.

## Run the Full Application Locally

The full application includes the frontend, API, worker, MySQL, and Redis.

### Requirements

- Docker
- Docker Compose
- Git

Clone the repository and enter the project directory:

```bash
git clone https://github.com/qwerty12-ai/knowledge-compiler.git
cd knowledge-compiler
```

Create the local environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure the database credentials and host user/group IDs.

On Linux or WSL, get your IDs with:

```bash
id -u
id -g
```

Set the corresponding values:

```dotenv
HOST_UID=YOUR_USER_ID
HOST_GID=YOUR_GROUP_ID
```

Configure the MySQL passwords in `.env` before starting the services. Keep this file private; it contains local configuration and may contain credentials.

Build and start the application:

```bash
docker compose up --build
```

### Local URLs

| Service                       | URL                                |
| ----------------------------- | ---------------------------------- |
| Web interface                 | http://localhost:3000              |
| API health check              | http://localhost:8000/health       |
| Interactive API documentation | http://localhost:8000/docs         |
| OpenAPI schema                | http://localhost:8000/openapi.json |

The API and worker use the internal Compose service names to reach MySQL and Redis. `docker-compose.yml` sets `NEXT_PUBLIC_API_URL` to `http://localhost:8000` for the frontend, and the frontend code falls back to the same address. The API's CORS configuration allows only the origin `http://localhost:3000`.

### Analyzing a repository through the web interface

The API and worker have access to the host user's home directory through a read-only mount at `/workspace`.

When submitting a repository for analysis, use its path as visible inside the container, not its original host path. For example, a host path such as:

```text
/home/your-user/projects/example
```

is accessible in the container as:

```text
/workspace/projects/example
```

The exact path depends on the repository's location under your home directory.

The analysis form has an AI investigation toggle. Its limit field is disabled until AI investigation is enabled, is pre-filled with 100, and must be a whole number of at least 1. With AI investigation off, the form submits no limit. The API responds with a 404 error if the submitted path does not exist, or is not a directory, inside the container.

### Stopping the application

Stop the running services:

```bash
docker compose down
```

To also remove Compose-managed volumes:

```bash
docker compose down -v
```

Warning: `docker compose down -v` removes the MySQL and Redis volumes managed by this Compose project. This can delete stored analyses and other persisted data. Do not use it unless you intend to reset that data.

### Ollama and Docker Compose

Ollama is not included as a service in the current Compose configuration. If you want to use AI investigation, Ollama must be available to the environment running the compiler. Configure the appropriate connection for your setup rather than assuming the model is automatically available inside the containers. This repository does not configure or test Ollama connectivity from the containers.

## Backend API

The current API exposes the following principal endpoints.

| Method | Endpoint                                | Purpose                                         |
| ------ | --------------------------------------- | ----------------------------------------------- |
| GET    | /                                       | API information and useful links                |
| GET    | /health                                 | Health check                                    |
| POST   | /api/v1/analyses                        | Queue a repository analysis                     |
| GET    | /api/v1/analyses                        | Retrieve recent analysis history                |
| GET    | /api/v1/analyses/{analysis_id}          | Retrieve analysis details                       |
| GET    | /api/v1/analyses/{analysis_id}/events   | Stream analysis events                          |
| GET    | /api/v1/analyses/{analysis_id}/claims   | Retrieve claims for an analysis                 |
| GET    | /api/v1/claims/{claim_id}               | Retrieve a claim                                |
| GET    | /api/v1/analyses/{analysis_id}/evidence | Retrieve evidence for an analysis               |
| GET    | /api/v1/redis/inspector/{analysis_id}   | Inspect Redis state associated with an analysis |

`POST /api/v1/analyses` accepts a JSON body with:

| Field             | Type    | Notes                                                                                   |
| ----------------- | ------- | --------------------------------------------------------------------------------------- |
| `repository_path` | string  | Required. Path as seen inside the API container (for example `/workspace/my-project`).  |
| `with_ai`         | boolean | Optional, default `false`.                                                              |
| `limit`           | integer | Optional, must be at least 1. Applied only to AI investigation units (see `--limit`).   |

`{analysis_id}` is the UUID returned when the analysis is queued. It resolves while the analysis state is held in Redis, which expires one hour after its last update. A completed analysis can also be addressed by its numeric database ID, which is also what `/api/v1/claims/{claim_id}` expects for claims.

For request and response schemas, open the interactive API documentation at [http://localhost:8000/docs](http://localhost:8000/docs) while the backend is running.

### Background processing

The API validates a submitted repository path, initializes the analysis state, and enqueues an analysis job. A worker processes the job, invokes the compiler, persists the results, and updates the analysis state.

Redis supports analysis state, job processing, and event delivery. MySQL stores the durable analysis data.

## Testing

Run the compiler tests:

```bash
python -m pytest compiler/tests/ -q
```

Run the backend tests from the repository root:

```bash
python -m pytest backend/tests/ -q
```

The backend tests need MySQL and Redis, with the schema from `database/schema.sql` loaded and the `MYSQL_*` and `REDIS_*` environment variables pointing at them; CI provides both as service containers. They also need the backend dependencies (`python -m pip install -r backend/requirements.txt`, plus `pytest` and `requests`, as CI installs them).

`backend/tests/test_integration.py` is different: it calls the running Docker stack at `http://localhost:8000` and submits an AI-enabled analysis (`limit` 1) of `/workspace/knowledge-compiler/compiler`. It is skipped when `RUN_DOCKER_AI_INTEGRATION=0`, which is how CI runs the backend tests. Without that variable the test runs and fails if the stack is not up:

```bash
RUN_DOCKER_AI_INTEGRATION=0 python -m pytest backend/tests/ -q
```

Run frontend checks:

```bash
cd frontend
npm ci
npm run lint
npm run build
```

The GitHub Actions workflow runs the project's compiler and backend tests, along with frontend lint and build checks. It also provisions MySQL and Redis for the relevant test jobs.

Test counts change as the project evolves; consult the latest test run rather than relying on a hard-coded number in this README.

## Repository Layout

```text
knowledge-compiler/
├── compiler/
│   ├── src/
│   │   └── knowledge_compiler/
│   ├── tests/
│   ├── pyproject.toml
│   └── README.md
├── backend/
│   ├── app/
│   ├── tests/
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── database/
│   └── schema.sql
├── docs/
│   ├── DEVELOPMENT.md
│   └── WHY_I_BUILT_THIS.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

This is a high-level view; individual modules and files may change as development continues.

## Security and Trust Boundaries

Knowledge Compiler analyzes source repositories, which must be treated as untrusted input.

Important boundaries include:

- **Repository paths:** Analyze only repositories you are authorized to inspect.
- **File access:** Discovery excludes common generated directories, skips symlinks, and ignores files above its configured size limit. These safeguards do not constitute a complete sandbox.
- **AI investigation:** Repository content sent to a local model may influence its observations. Model output must be treated as untrusted and checked against source evidence.
- **Local infrastructure:** MySQL and Redis are development services. Do not expose their ports or credentials to untrusted networks.
- **Environment files:** Keep `.env` and other secrets out of version control.
- **Container mounts:** The API and worker receive a read-only mount of the host user's home directory. Read-only access prevents writes through that mount, but it does not make arbitrary repository analysis a complete security sandbox.

Do not run this project against hostile repositories on a machine containing sensitive data unless you have established suitable isolation.

## Known Limitations

Knowledge Compiler is an evolving engineering project, not a universal code-understanding system.

Current limitations include:

- Structural extraction is primarily implemented for Python, even though file discovery recognizes additional programming languages.
- Deterministic claims cover a limited set of repository properties.
- Optional AI investigation examines selected units rather than reasoning exhaustively about every possible behavior.
- Local AI investigation can be slow on CPU-only hardware.
- AI investigation covers `README.md` documentation, Python functions, and Python classes. Test files are not investigated.
- Observation validation is performed by the same local model that produced the observations, and the evidence attached to an AI-derived claim is the independently extracted evidence from the same source file, not a line-level citation.
- `--limit` has no effect without `--with-ai`, and the CLI currently accepts that combination without a warning.
- Baseline claims about files that are not `README.md`, test, or dependency files are worded "The repository contains source code in <path>", including for Markdown, JSON, and YAML files.
- Directory exclusions are matched against every component of the path discovery walks, including the parent directories of the repository when an absolute path is used. A repository stored under a directory named, for example, `build` or `out` may be discovered as empty.
- Validation compares observations with available extracted evidence; it cannot prove arbitrary program behavior.
- Confidence scores are heuristic and are not calibrated probabilities.
- The current claim-generation path does not assign every status defined by the knowledge model.
- Repository-local IDs in compiler JSON output are not persistent database identifiers.
- The CLI and web application's stored analysis history are separate workflows.
- The system does not yet provide a complete semantic model of an entire codebase.

These limitations are part of the engineering problem the project is intended to explore.

## Documentation

- [`compiler/README.md`](compiler/README.md) — compiler architecture, extraction pipeline, claims, evidence, and CLI behavior.
- [`docs/WHY_I_BUILT_THIS.md`](docs/WHY_I_BUILT_THIS.md) — the motivation behind the project.
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) — local setup, services, tests, and development workflow.
- [`LICENSE`](LICENSE) — license terms.

## Feedback

If you have used Knowledge Compiler and hit an issue, an unexpected result, or have a useful improvement, thoughtful feedback is welcome. Please report it through the repository's GitHub page. If possible, include:

- What you were trying to do.
- The steps required to reproduce the behavior.
- Your operating system and relevant environment details.
- The expected result and the actual result.
- Sanitized logs or error messages, with secrets and sensitive source material removed.

Feedback does not grant permission to use, modify, redistribute, or commercially exploit the project.

## License

Knowledge Compiler is proprietary software. All rights are reserved by the copyright holder.

Unless expressly authorized in writing by the copyright holder or required by applicable law, no permission is granted to use, reproduce, modify, redistribute, sublicense, or commercially exploit this software. See [`LICENSE`](LICENSE) for the full notice.

The repository is publicly viewable on GitHub. Public visibility does not mean the project is released under an open-source license.

## Project Direction

The long-term goal is to help engineers investigate unfamiliar software systems by making repository-derived knowledge easier to discover, evaluate, and trace back to its sources.

The guiding principle remains:

Show the evidence. Make uncertainty visible. Never confuse a plausible explanation with an established fact.
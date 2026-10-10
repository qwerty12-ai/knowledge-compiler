# Development Guide

This document explains how to set up Knowledge Compiler locally, run its services, execute tests, and troubleshoot common development problems.

The project consists of a Python compiler, a FastAPI backend, a background worker, MySQL, Redis, and a Next.js frontend.

The standalone compiler can be developed independently. The full application requires the supporting infrastructure.

The repository has two ways to run an analysis:

1. **Direct CLI analysis** — run the compiler as a local Python process.
2. **Web analysis** — submit an analysis through the web interface, with the work performed by the API and worker containers.

These workflows are related but not interchangeable. A CLI analysis run on the host does not automatically appear in the web application's analysis history.

---

## 1. Prerequisites

Install the following tools before starting.

| Tool | Requirement | Purpose |
|---|---|---|
| Python | 3.14+ | Compiler and backend |
| Node.js | 20 | Frontend development (CI and the frontend Docker image use Node.js 20) |
| npm | Compatible with the frontend lockfile | Frontend dependencies |
| Docker | Docker Engine or Docker Desktop | Containerized services |
| Docker Compose | Compose v2 | Local orchestration |
| Git | Recent version | Source control |
| Cairo library | `libcairo2` on Debian, Ubuntu, WSL | Native dependency of CairoSVG, which the compiler imports for its terminal banner; the backend Docker image installs it |
| Ollama | Optional | Local AI investigation |

The compiler requires Python 3.14 or newer according to its package configuration.

You do not need Ollama or a GPU to run deterministic compiler analysis.

## 2. Repository Structure

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

The exact contents of individual directories may change as the project evolves.

## 3. Clone the Repository

```bash
git clone https://github.com/qwerty12-ai/knowledge-compiler.git
cd knowledge-compiler
```

Run subsequent commands from the repository root unless a section explicitly tells you to enter a subdirectory.

## 4. Develop the Compiler Independently

The Python compiler can be installed and used without starting the frontend, backend, MySQL, or Redis.

### Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Install the compiler

From the repository root:

```bash
python -m pip install -e "./compiler[dev]"
```

This installs the compiler in editable mode along with its development dependencies.

### Run an analysis

Analyze the current repository:

```bash
knowledge-compiler analyze .
```

Analyze a different repository:

```bash
knowledge-compiler analyze /path/to/repository
```

### Generate JSON output

```bash
knowledge-compiler analyze /path/to/repository --json
```

Generate compact JSON (`--json` and `--compact-json` are mutually exclusive):

```bash
knowledge-compiler analyze /path/to/repository --compact-json
```

Write the result to a file:

```bash
knowledge-compiler analyze /path/to/repository --json --output analysis.json
```

`--output` always writes JSON to the file (compact with `--compact-json`, full otherwise), whether or not `--json` is given.

### Enable AI investigation

Install and start Ollama separately, then download the configured model:

```bash
ollama pull qwen3:4b
```

Run:

```bash
knowledge-compiler analyze /path/to/repository --with-ai
```

Limit the number of units considered for AI investigation:

```bash
knowledge-compiler analyze /path/to/repository --with-ai --limit 10
```

#### The `--limit` option

- `--limit N` limits the number of units considered for AI investigation. It does not limit the number of files discovered.
- Deterministic analysis does not require AI, and `--limit` plays no part in it.
- `N` must be an integer of at least 1; smaller values are rejected, with or without `--with-ai`.
- It is applied only inside the AI investigation path (`compiler/src/knowledge_compiler/pipeline.py`). If you pass `--limit` without `--with-ai`, the CLI accepts the command and runs the deterministic analysis; the limit is not applied. The value is still recorded in the result's `limit` field. The CLI does not currently reject or warn about this combination, and no compiler test currently exercises `--limit` through the CLI.
- Units are taken in build order: README documentation first, then each Python file's functions and classes in path order.
- The web interface enables its limit field only when AI investigation is on (pre-filled with 100) and submits no limit when it is off.

If you change this behavior (for example by making the CLI reject the combination), update the documentation and add a test in the same change.

For available CLI options, run:

```bash
knowledge-compiler analyze --help
```

### AI investigation performance

AI investigation is optional and can be much slower than deterministic analysis.

In CPU-only testing, one AI investigation unit has taken roughly **2–3 minutes**. This is an observed estimate on one setup, not a benchmark or a guaranteed duration. For illustration, 100 units processed sequentially at that rate would take about 200–300 minutes (roughly 3 hours 20 minutes to 5 hours), before overhead and differences in model behavior.

A capable GPU can reduce inference time substantially, depending on the GPU, available memory, model, and runtime configuration; no particular speedup is guaranteed. Use `--limit` to keep CPU-only runs manageable. The web interface pre-fills its limit field with 100.

## 5. Configure the Full Application

The full application runs through Docker Compose.

### Create the environment file

From the repository root:

```bash
cp .env.example .env
```

Edit `.env` and configure the MySQL credentials and host user/group IDs.

The example configuration contains these settings:

```dotenv
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=knowledge_compiler
MYSQL_USER=knowledge_compiler
MYSQL_PASSWORD=
MYSQL_ROOT_PASSWORD=

REDIS_HOST=127.0.0.1
REDIS_PORT=6379

NEXT_PUBLIC_API_URL=http://localhost:8000

HOST_UID=
HOST_GID=
```

Set strong, local development passwords for MySQL before starting the application.

`docker-compose.yml` passes `.env` to the `api` and `worker` services through `env_file`. The `frontend` service does not read `.env`: its `NEXT_PUBLIC_API_URL` is set directly in `docker-compose.yml`, and the frontend code falls back to the same default (`http://localhost:8000`). Next.js normally embeds `NEXT_PUBLIC_*` values when the app is built, and the frontend Dockerfile does not pass this variable as a build argument, so do not expect a change in `.env` to alter where the built frontend sends requests.

### Configure host user and group IDs

On Linux or WSL, run:

```bash
id -u
id -g
```

Set the returned values in `.env`:

```dotenv
HOST_UID=YOUR_USER_ID
HOST_GID=YOUR_GROUP_ID
```

`docker-compose.yml` requires both values: the `api` and `worker` services run as this user so that they can read the mounted home directory. Compose refuses to start if either is missing.

Do not commit `.env` or share it publicly. Keep credentials and other secrets out of version control.

### Environment variable considerations

The `api` and `worker` services override `MYSQL_HOST` and `REDIS_HOST` in `docker-compose.yml` so that they connect to the `mysql` and `redis` services by their Compose hostnames. The loopback addresses in `.env.example` are for processes running directly on the host.

Inside a container, `localhost` refers to that container itself, not another service.

If a connection fails, inspect the environment variables consumed by the relevant service and the service-specific configuration before changing application code.

## 6. Start the Application

Build the images and start the services:

```bash
docker compose up --build
```

To start the services in the background:

```bash
docker compose up --build -d
```

Inspect the running services:

```bash
docker compose ps
```

Follow the logs:

```bash
docker compose logs -f
```

Follow logs for an individual service:

```bash
docker compose logs -f api
docker compose logs -f worker
docker compose logs -f frontend
docker compose logs -f mysql
docker compose logs -f redis
```

These are the service names defined in the current `docker-compose.yml`.

### Local application URLs

| Component                     | URL                                |
| ----------------------------- | ---------------------------------- |
| Frontend                      | http://localhost:3000              |
| API health check              | http://localhost:8000/health       |
| Interactive API documentation | http://localhost:8000/docs         |
| OpenAPI schema                | http://localhost:8000/openapi.json |

Open the frontend in your browser after the services have started. If a service is still initializing, give it time to become healthy and inspect its logs if it fails to start.

## 7. How the Services Work Together

The application separates HTTP request handling from repository analysis.

A typical web analysis follows this sequence:

- The frontend submits a repository path to the API.
- The API validates the request and initializes the analysis state.
- The API enqueues a background job.
- Redis and BullMQ support job processing and analysis state.
- The worker retrieves the job and invokes the Python compiler.
- The worker persists the analysis results in MySQL.
- The frontend retrieves analysis details, claims, and evidence.
- Server-sent events provide analysis progress updates.

This architecture prevents long-running analysis work from needing to execute directly inside the HTTP request handler.

### Database

MySQL stores durable analysis information, including:

- Analyses
- Claims
- Evidence
- Claim-evidence relationships

The schema is maintained in:

```text
database/schema.sql
```

The schema defines relationships between the records, including foreign-key constraints.

### Redis

Redis supports the background processing and analysis-state workflows.

The project also includes a Redis Inspector interface for inspecting relevant analysis state and queue-related information.

Analysis state in Redis expires one hour after its last update. The `analysis_id` UUID returned when an analysis is queued therefore stops resolving after that; use the numeric database ID (shown in the analysis history) for completed analyses.

Redis is not a replacement for the durable analysis records stored in MySQL.

### CLI versus web analysis paths

When you run the CLI directly:

```bash
knowledge-compiler analyze ./compiler
```

the path is resolved by the host process relative to the current working directory. The result is local to that run; it is not submitted to the web application or added to its history.

When you submit an analysis through the web interface, the `api` and `worker` containers must be able to see the path. They receive a read-only mount of the host user's home directory at `/workspace`, so a repository at:

```text
/home/your-user/knowledge-compiler/compiler
```

is submitted as:

```text
/workspace/knowledge-compiler/compiler
```

A host path such as `./compiler` or `/home/your-user/...` is not a valid container path. Before submitting, confirm that the directory exists, lies under your home directory, and that the path you enter is the `/workspace/...` form. The API responds with a 404 error if the path does not exist, or is not a directory, inside the container.

The analysis form's limit field is disabled until the AI investigation toggle is on, and the form submits no limit when AI investigation is off. The API itself accepts `limit` (at least 1) with or without `with_ai`.

Security note: A read-only mount prevents writes through that mount, but it is not a complete sandbox for untrusted repository analysis. Use suitable isolation when analyzing repositories you do not trust.

### Ollama

Ollama is not included as a service in the current Compose configuration.

If AI investigation is enabled, the model service must be reachable from the environment in which the compiler runs. A model installed on the host is not automatically reachable through `localhost` from inside a container.

Configure the model connection appropriately for your environment. The compiler creates the Ollama client with its default settings and does not set a host itself, and this repository does not configure or test Ollama connectivity from the containers. Do not assume that AI investigation will work in the full application without configuring it.

## 8. Running Tests

Run tests after changing compiler behavior, backend functionality, or shared interfaces.

### Compiler tests

From the repository root:

```bash
python -m pytest compiler/tests/ -q
```

The compiler tests cover the analysis pipeline, evidence extraction, claim generation, serialization, CLI behavior, and related functionality.

### Backend tests

From the repository root:

```bash
python -m pytest backend/tests/ -q
```

The backend tests need MySQL and Redis, with the schema from `database/schema.sql` loaded and the `MYSQL_*` and `REDIS_*` environment variables pointing at them. CI provides both as service containers. Install the backend dependencies first (`python -m pip install -r backend/requirements.txt`, plus `pytest` and `requests`, as CI does).

`backend/tests/test_integration.py` is different: it calls the running Docker stack at `http://localhost:8000` and submits an AI-enabled analysis (`limit` 1) of `/workspace/knowledge-compiler/compiler`. It is skipped when `RUN_DOCKER_AI_INTEGRATION=0`, which is how CI runs the backend tests. Without that variable it runs, and fails if the stack is not up:

```bash
RUN_DOCKER_AI_INTEGRATION=0 python -m pytest backend/tests/ -q
```

Do not assume that a test requiring external services will pass with those services stopped.

### Frontend lint

```bash
cd frontend
npm ci
npm run lint
```

### Frontend production build

```bash
npm run build
```

Run both frontend checks after changing components, API integration, or application routing. The frontend defines `dev`, `build`, `start`, and `lint` scripts; it does not currently define a test script.

### Suggested validation sequence

After a compiler-only change:

```bash
python -m pytest compiler/tests/ -q
```

After a backend change:

```bash
python -m pytest compiler/tests/ -q
python -m pytest backend/tests/ -q
```

After a frontend change:

```bash
cd frontend
npm run lint
npm run build
```

After changes spanning the application, run the relevant test suites and validate the full application through Docker Compose.

A successful unit-test run does not automatically establish that all services integrate correctly.

## 9. Continuous Integration

The GitHub Actions workflow is located at:

```text
.github/workflows/ci.yml
```

The workflow runs on pushes and pull requests targeting the `main` branch.

The current workflow includes:

- Python 3.14 setup.
- Compiler dependency installation and tests.
- Backend dependency installation (`backend/requirements.txt`, plus `pytest` and `requests`).
- MySQL 8.4 and Redis 7 service containers.
- Database schema initialization.
- Backend tests.
- Node.js 20 setup.
- Frontend dependency installation.
- Frontend linting.
- Frontend production build.

The backend CI step sets `RUN_DOCKER_AI_INTEGRATION=0`. This avoids making the ordinary CI run depend on a local Ollama model.

The current workflow does not build every Docker image as part of CI.

When adding a new service, dependency, or integration test, update the workflow if the new requirement must be validated automatically.

## 10. Database Initialization and Resetting Data

The Compose configuration initializes the MySQL schema from:

```text
database/schema.sql
```

Initialization scripts are generally applied when the MySQL data directory is first initialized. Editing the schema file does not necessarily update an existing database volume.

If the database already exists, use an intentional migration or database reset procedure rather than assuming Compose will recreate the schema automatically.

### Stop the application

```bash
docker compose down
```

This stops and removes the Compose containers and network while normally preserving named volumes.

### Reset persistent data

```bash
docker compose down -v
```

Warning: This removes Compose-managed volumes, including the MySQL and Redis data stored in those volumes. Existing analyses and other persisted information may be lost.

Only run this command when you deliberately want to discard the local persisted state.

Do not use volume deletion as the default solution to a database problem.

## 11. Troubleshooting

### The CLI command is not found

Ensure the virtual environment is active:

```bash
source .venv/bin/activate
```

Reinstall the compiler in editable mode:

```bash
python -m pip install -e "./compiler[dev]"
```

Confirm that the command is available:

```bash
knowledge-compiler --help
```

### The compiler rejects a repository path

Check that the path exists and points to a directory.

For the web application, remember that paths must be valid inside the API and worker containers (the `/workspace/...` form), not merely on the host machine.

### `--limit` seems to have no effect

`--limit` applies only to AI investigation. Without `--with-ai` the CLI accepts it but does not apply it, and the value is only recorded in the result. With `--with-ai`, check that the repository actually has README documentation, Python functions, or Python classes to investigate (test files are not investigated).

### The compiler rejects `--limit`

`--limit` must be an integer of at least 1.

### The CLI result does not appear in the web application

This is expected. Host-side CLI analysis and web-submitted analysis are separate workflows.

### AI investigation fails

Check that:

- Ollama is installed and running.
- The configured model has been pulled.
- The model name matches the compiler configuration.
- The compiler can reach the Ollama service.
- The machine has sufficient memory and compute resources.

Verify that the model is available to Ollama:

```bash
ollama list
```

AI investigation is optional. Run without `--with-ai` to test the deterministic analysis path independently.

### AI investigation is very slow

CPU-only inference can take minutes per unit. Check the hardware available to Ollama and reduce the workload with `--limit`. See the performance notes in section 4.

### The API cannot connect to MySQL

Inspect the API and MySQL logs:

```bash
docker compose logs -f api
docker compose logs -f mysql
```

Verify the database host, port, database name, username, and password.

Inside Compose, the API should use the configured service hostname rather than assuming the database is available at the container's own `127.0.0.1`.

### The API cannot connect to Redis

Inspect the API, worker, and Redis logs:

```bash
docker compose logs -f api
docker compose logs -f worker
docker compose logs -f redis
```

Verify that the services use the expected Redis hostname and port.

### The CLI fails on startup with a Cairo error

The compiler imports CairoSVG for its terminal banner, which needs the Cairo system library. On Debian, Ubuntu, and WSL, install `libcairo2`.

### The frontend cannot reach the API

Check the frontend's `NEXT_PUBLIC_API_URL` configuration and verify that the API is available at:

```text
http://localhost:8000/health
```

Remember that browser-side requests and container-to-container requests use different networking contexts. The API's CORS configuration allows only the origin `http://localhost:3000`, so a frontend served from another origin will be blocked by the browser.

A hostname that resolves inside a container may not resolve in the browser, and vice versa.

### A database schema change does not appear

Check whether MySQL is reusing an existing data volume.

Initialization scripts do not automatically act as migrations for an already initialized database. Apply the required schema change intentionally.

### Docker containers fail because of filesystem permissions

Check the configured `HOST_UID` and `HOST_GID` values:

```bash
id -u
id -g
```

Compare these values with the settings in `.env` and inspect the API or worker logs.

Avoid changing filesystem permissions recursively as a first response. Identify which process and mount are producing the error.

### Tests fail only when run in isolation

Some backend tests depend on infrastructure, environment variables, or shared test setup.

Inspect the failing test and its fixtures, verify that required services are available, and follow the existing test configuration before changing application code.

## 12. Development Principles

### Preserve the pipeline boundaries

Discovery, evidence extraction, optional AI investigation, validation, and claim generation have distinct responsibilities.

Avoid placing unrelated behavior into one large function when it belongs in a dedicated stage.

### Keep deterministic analysis independent of AI

Basic repository analysis should remain useful without a language model.

AI-generated observations must not be treated as independently verified evidence.

### Make uncertainty explicit

When evidence is insufficient, preserve the unknown state instead of inventing support.

A plausible explanation is not the same as an established engineering fact.

### Test failure paths

Test more than the happy path.

Consider invalid paths, unreadable files, unavailable AI services, incomplete evidence, failed jobs, serialization errors, and database or Redis connection failures where applicable.

### Preserve existing behavior

Before modifying a shared API contract, database relationship, Redis lifecycle, or frontend data flow, inspect the existing implementation and tests.

Prefer targeted changes over broad rewrites.

### Keep documentation synchronized

When changing CLI options, result schemas, service configuration, or API behavior, update the relevant documentation in the same change.

Documentation should describe implemented behavior, not aspirational behavior.

## 13. Before Opening a Pull Request

Use this checklist when preparing a change.

- The change has a clearly defined purpose.
- Existing implementation and related tests have been inspected.
- Relevant tests pass.
- Frontend lint and build pass when the frontend is affected.
- Integration tests pass when service interactions are affected.
- No secrets or local environment files are committed.
- API, schema, and configuration changes are documented.
- Existing functionality has not been removed unintentionally.
- The change does not present unsupported AI conclusions as verified facts.

The objective is not merely to make the tests green. It is to preserve a system whose behavior is understandable, testable, and grounded in evidence.

## 14. License

Knowledge Compiler is proprietary software; see [`../LICENSE`](../LICENSE). The repository is publicly viewable, but public visibility is not an open-source license. For project motivation and design principles, see [Why I Built This](WHY_I_BUILT_THIS.md).
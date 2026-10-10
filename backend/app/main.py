from pathlib import Path
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .models import (
    AnalysisRequest,
    AnalysisCreatedResponse,
    AnalysisStatusResponse,
    ClaimsResponse,
    ClaimDetailResponse,
    EvidenceResponse,
    AnalysisHistoryResponse,
    RedisInspectorResponse,
)
from .services.analysis import analyze_repository
from .services.redis_state import (
    get_analysis_state,
    set_analysis_state,
)
from .services.analysis_identity import resolve_database_id
from .services.redis_inspector import (
    inspect_analysis_state,
    inspect_analysis_queue,
    inspect_analysis_channel,
)
from .services.redis_subscriber import stream_analysis_events
from .queue import get_analysis_queue
from .services.results import (
    get_analysis_claims,
    get_claim_with_evidence,
    get_analysis_evidence,
    get_recent_analyses,
    get_analysis,
)


app = FastAPI(
    title="Knowledge Compiler API",
    description=(
        "API for analyzing repositories and "
        "inspecting engineering knowledge."
    ),
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def root() -> dict:
    return {
        "name": "Knowledge Compiler API",
        "version": app.version,
        "description": (
            "Turn codebases into structured engineering "
            "knowledge backed by evidence."
        ),
        "status": "running",
        "links": {
            "documentation": "/docs",
            "openapi_schema": "/openapi.json",
            "health": "/health",
        },
        "capabilities": [
            "Repository discovery",
            "Evidence extraction",
            "Claim generation",
            "Evidence-backend investigation",
        ],
        "message": (
            "Welcome to Knowledge Compiler."
            " Explore the API documentation to get started."
        ),
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/api/v1/analyses",
    response_model=AnalysisCreatedResponse,
)
async def create_analysis(
    request: AnalysisRequest,
) -> dict:
    repository_path = (
        Path(request.repository_path)
        .expanduser()
        .resolve()
    )

    if not repository_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Repository path does not exist.",
        )

    if not repository_path.is_dir():
        raise HTTPException(
            status_code=404,
            detail="Repository path is not a directory.",
        )

    analysis_id = str(uuid.uuid4())

    set_analysis_state(
        analysis_id=analysis_id,
        status="queued",
        stage="queued",
        progress=0,
    )

    queue = get_analysis_queue()
    try:
        job = await queue.add(
            "analyze-repository",
            {
                "repository_path": str(repository_path),
                "analysis_id": analysis_id,
                "limit": request.limit,
                "with_ai": request.with_ai,
            },
        )
    finally:
        await queue.close()


    return {
        "analysis_id": analysis_id,
        "job_id": job.id,
        "status": "queued",
    }


@app.get(
    "/api/v1/analyses/{analysis_id}/events",
)
def analysis_events(
    analysis_id: str,
) -> StreamingResponse:
    return StreamingResponse(
        stream_analysis_events(analysis_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get(
    "/api/v1/analyses/{analysis_id}",
    response_model=AnalysisStatusResponse,
)
def get_analysis_endpoint(
    analysis_id: str,
) -> dict:
    state = get_analysis_state(analysis_id)

    if state:
        return {
            "analysis_id": analysis_id,
            **state,
        }

    try:
        database_id = int(analysis_id)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    analysis = get_analysis(database_id)

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    return {
        "analysis_id": analysis_id,
        "status": "completed",
        "stage": "completed",
        "progress": 100,
        "database_id": analysis["id"],
        "repository_path": analysis["repository_path"],
        "files_discovered": analysis["files_discovered"],
        "with_ai": analysis["with_ai"],
        "analysis_limit": analysis["analysis_limit"],
    }


@app.get(
    "/api/v1/analyses/{analysis_id}/claims",
    response_model=ClaimsResponse,
)
def get_claims(
    analysis_id: str,
) -> dict:
    database_id = resolve_database_id(analysis_id)

    if database_id is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    claims = get_analysis_claims(database_id)

    return {
        "analysis_id": analysis_id,
        "claims": claims,
    }


@app.get(
    "/api/v1/claims/{claim_id}",
    response_model=ClaimDetailResponse,
)
def get_claim(
    claim_id: int,
) -> dict:
    claim = get_claim_with_evidence(claim_id)

    if claim is None:
        raise HTTPException(
            status_code=404,
            detail="Claim not found.",
        )

    return claim


@app.get(
    "/api/v1/analyses/{analysis_id}/evidence",
    response_model=EvidenceResponse,
)
def get_evidence(
    analysis_id: str,
) -> dict:
    database_id = resolve_database_id(analysis_id)

    if database_id is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    evidence = get_analysis_evidence(database_id)

    return {
        "analysis_id": analysis_id,
        "evidence": evidence,
    }


@app.get(
    "/api/v1/analyses",
    response_model=AnalysisHistoryResponse,
)
def get_recent_analysis_history() -> dict:
    analyses = get_recent_analyses()

    return {
        "analyses": analyses,
    }


@app.get(
    "/api/v1/redis/inspector/{analysis_id}",
    response_model=RedisInspectorResponse,
)
async def inspect_redis(
    analysis_id: str,
) -> dict:
    state = inspect_analysis_state(analysis_id)
    queue = await inspect_analysis_queue()
    channel = inspect_analysis_channel()

    return {
        "state": state,
        "queue": queue,
        "channel": channel,
    }
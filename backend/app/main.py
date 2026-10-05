from fastapi import FastAPI
from .models import AnalysisRequest
from .services.analysis import analyze_repository
from .queue import get_analysis_queue
import uuid
from .services.redis_inspector import inspect_analysis_state, inspect_analysis_queue, inspect_analysis_channel

app = FastAPI(
    title="Knowledge Compiler API",
    description="API for analyzing repositories and inspecting engineering knowledge.",
    version="0.1.0"
)

@app.get("/", include_in_schema=False)
def root() -> dict:
    return {
        "name": "Knowledge Compiler API",
        "version": app.version,
        "description": (
            "Turn codebases into structured engineering knowledge "
            "backed by evidence."
        ),
        "status": "running",
        "links": {
            "documentation": "/docs",
            "openapi_schema": "/openapi.json",
            "health": "/health"
        },
        "capabilities": [
            "Repository discovery",
            "Evidence extraction",
            "Claim generation",
            "Evidence-backend investigation"
        ],
        "message": (
            "Welcome to Knowledge Compiler."
            " Explore the API documentation to get started."
        )
    }

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/api/v1/analyses")
async def create_analysis(request: AnalysisRequest) -> dict:
    analysis_id = str(uuid.uuid4())
    queue = get_analysis_queue()
    job = await queue.add(
        "analyze-repository",
        {
            "repository_path": request.repository_path,
            "analysis_id": analysis_id,
            "limit": request.limit,
            "with_ai": request.with_ai 
        }
    )

    return {
        "analysis_id": analysis_id,
        "job_id": job.id,
        "status": "queued"
    }

@app.get("/api/v1/redis/inspector/{analysis_id}")
async def inspect_redis(analysis_id: str) -> dict:
    state = inspect_analysis_state(analysis_id)
    queue = await inspect_analysis_queue()
    channel = inspect_analysis_channel()

    return {
        "state": state,
        "queue": queue,
        "channel": channel
    }
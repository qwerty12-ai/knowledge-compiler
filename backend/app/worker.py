import asyncio
from bullmq import Worker
from backend.app.queue import ANALYSIS_QUEUE_NAME
from backend.app.services.redis_state import set_analysis_state
from backend.app.services.analysis import analyze_repository
from backend.app.models import AnalysisRequest

async def process_analysis_job(job, token):
    print(f"Processing job: {job.id}")
    print(f"Job data: {job.data}")

    repository_path = job.data["repository_path"]
    analysis_id = job.data["analysis_id"]

    set_analysis_state(
        analysis_id=analysis_id,
        status="running",
        stage="analysis",
        progress=20
    )

    request = AnalysisRequest(
        repository_path=repository_path,
        limit=job.data.get("limit", 100),
        with_ai=job.data.get("with_ai", False)
    )

    result = await asyncio.to_thread(
        analyze_repository,
        request
    )

    set_analysis_state(
        analysis_id=analysis_id,
        status="completed",
        stage="completed",
        progress=100
    )   

    return {
        "status": "processed",
        "job_id": job.id
    }

async def create_analysis_worker():
    worker = Worker(
        ANALYSIS_QUEUE_NAME,
        process_analysis_job
    )

    return worker
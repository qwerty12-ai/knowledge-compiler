import asyncio
import traceback

from bullmq import Worker

from .models import AnalysisRequest
from .queue import ANALYSIS_QUEUE_NAME
from .services.analysis import analyze_repository
from .services.redis_state import set_analysis_state


async def process_analysis_job(job, token):
    print(f"Processing job: {job.id}")
    print(f"Job data: {job.data}")

    repository_path = job.data["repository_path"]
    analysis_id = job.data["analysis_id"]

    set_analysis_state(
        analysis_id=analysis_id,
        status="running",
        stage="discovery",
        progress=5,
    )

    try:
        request = AnalysisRequest(
            repository_path=repository_path,
            limit=job.data.get("limit", 100),
            with_ai=job.data.get("with_ai", False),
        )

        database_id = await asyncio.to_thread(
            analyze_repository,
            request,
            analysis_id,
        )

    except Exception as error:
        print(f"Analysis {analysis_id} failed: {error}")
        traceback.print_exc()

        set_analysis_state(
            analysis_id=analysis_id,
            status="failed",
            stage="failed",
            progress=20,
        )

        raise

    set_analysis_state(
        analysis_id=analysis_id,
        status="completed",
        stage="completed",
        progress=100,
        database_id=database_id,
    )

    return {
        "status": "processed",
        "job_id": job.id,
    }


async def create_analysis_worker():
    worker = Worker(
        ANALYSIS_QUEUE_NAME,
        process_analysis_job,
    )

    return worker
import asyncio
import uuid
from backend.app.queue import get_analysis_queue
from backend.app.worker import create_analysis_worker
from backend.app.services.redis_state import set_analysis_state, get_analysis_state

async def test_worker_processes_analysis_job():
    queue = get_analysis_queue()
    worker = await create_analysis_worker()

    job_id = f"test-worker-{uuid.uuid4()}"
    analysis_id = f"test-analysis-{uuid.uuid4()}"

    try:
        set_analysis_state(
            analysis_id=analysis_id,
            status="queued",
            stage="queued",
            progress=0
        )

        job = await queue.add(
            "analyze-repository",
            {
                "repository_path": "./compiler",
                "analysis_id": analysis_id,
                "limit": 100
            },
            {
                "jobId": job_id,
                "attempts": 3,
                "backoff": {
                    "type": "fixed",
                    "delay": 100
                }
            }
        )

        for _ in range(50):
            processed_job = await queue.getJob(job.id)

            if processed_job is not None:
                state = await processed_job.getState()
                print("JOB STATE: ", state)
                if state == "completed":
                    break

            await asyncio.sleep(0.1)

        assert processed_job is not None
        assert await processed_job.getState() == "completed"
        analysis_state = get_analysis_state(analysis_id)
        print("ANALYSIS STATE: ", analysis_state)
        assert analysis_state["status"] == "completed"
        assert analysis_state["stage"] == "completed"
        assert analysis_state["progress"] == "100"
    finally:
        await worker.close()
        await queue.close()
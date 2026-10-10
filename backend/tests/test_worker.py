import asyncio
import uuid
import pytest
from backend.app import worker
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
                "repository_path": "/workspace/knowledge-compiler/compiler",
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

async def test_worker_marks_analysis_failed(monkeypatch):
    analysis_id = f"test-analysis-failure-{uuid.uuid4()}"

    class FakeJob:
        id = f"test-worker-failure-{uuid.uuid4()}"
        data = {
            "repository_path": "./compiler",
            "analysis_id": analysis_id,
            "limit": 100,
        }

    def fake_analyze_repository(request, analysis_id):
        raise RuntimeError("Test analysis failure")

    monkeypatch.setattr(
        worker,
        "analyze_repository",
        fake_analyze_repository,
    )

    job = FakeJob()

    try:
        with pytest.raises(RuntimeError, match="Test analysis failure"):
            await worker.process_analysis_job(job, None)

        analysis_state = get_analysis_state(analysis_id)

        assert analysis_state["status"] == "failed"
        assert analysis_state["stage"] == "failed"
        assert analysis_state["progress"] == "20"

    finally:
        from backend.app.redis import get_redis_connection

        redis = get_redis_connection()
        redis.delete(f"analysis:{analysis_id}")
        redis.close()
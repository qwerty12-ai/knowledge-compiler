import asyncio
import time
import uuid
from pathlib import Path

import pytest
from bullmq import Queue

from backend.app import worker as worker_module
from backend.app.queue import get_redis_options
from backend.app.services.redis_state import set_analysis_state, get_analysis_state

# Resolved from this file, so it is valid on a developer machine, in WSL,
# and on the GitHub Actions runner. It is NOT a path inside the Docker
# container (/workspace/...).
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def isolated_queue_name(monkeypatch):
    """Use a private queue so only this test's worker can take the job.

    The real "analysis" queue is shared with the Docker `worker` container
    (Redis is published on localhost:6379) and with jobs left behind by other
    tests. Either of those can pick up our job, and a container cannot see
    host paths such as /home/<user>/... .
    """
    name = f"analysis-test-{uuid.uuid4()}"

    monkeypatch.setattr(worker_module, "ANALYSIS_QUEUE_NAME", name)
    return name


async def test_worker_processes_analysis_job(isolated_queue_name):
    queue = Queue(isolated_queue_name, {"connection": get_redis_options()})
    analysis_worker = await worker_module.create_analysis_worker()

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
                "repository_path": str(REPOSITORY_ROOT / "compiler"),
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

        processed_job = None
        state = None
        deadline = time.monotonic() + 15

        while time.monotonic() < deadline:
            processed_job = await queue.getJob(job.id)

            if processed_job is not None:
                state = await processed_job.getState()
                if state in {"completed", "failed"}:
                    break

            await asyncio.sleep(0.1)

        assert processed_job is not None
        assert state == "completed", (
            f"job ended as {state!r}: "
            f"{getattr(processed_job, 'failedReason', None)}"
        )

        analysis_state = get_analysis_state(analysis_id)
        assert analysis_state["status"] == "completed"
        assert analysis_state["stage"] == "completed"
        assert analysis_state["progress"] == "100"
    finally:
        await analysis_worker.close()
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
        worker_module,
        "analyze_repository",
        fake_analyze_repository,
    )

    job = FakeJob()

    try:
        with pytest.raises(RuntimeError, match="Test analysis failure"):
            await worker_module.process_analysis_job(job, None)

        analysis_state = get_analysis_state(analysis_id)

        assert analysis_state["status"] == "failed"
        assert analysis_state["stage"] == "failed"
        assert analysis_state["progress"] == "20"

    finally:
        from backend.app.redis import get_redis_connection

        redis = get_redis_connection()
        redis.delete(f"analysis:{analysis_id}")
        redis.close()
import pytest
from backend.app.queue import get_analysis_queue

async def test_add_analysis_job_to_queue():
    queue = get_analysis_queue()

    try:
        job = await queue.add(
            "analyze-repository",
            {
                "repository_path": "./compiler"
            }
        )
        assert job.id is not None
        assert job.name == "analyze-repository"
        assert job.data["repository_path"] == "./compiler"
    finally:
        await queue.close()
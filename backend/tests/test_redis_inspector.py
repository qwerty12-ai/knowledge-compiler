import pytest
from backend.app.services.redis_inspector import inspect_analysis_state, inspect_analysis_queue, inspect_analysis_channel 
from backend.app.services.redis_state import set_analysis_state, ANALYSIS_CHANNEL
from backend.app.services.redis_subscriber import get_analysis_events
from backend.app.queue import get_analysis_queue

def test_inspect_analysis_state():
    analysis_id = "test-inspector"

    set_analysis_state(
        analysis_id=analysis_id,
        status="running",
        stage="analysis",
        progress=20,
    )

    result = inspect_analysis_state(analysis_id)

    assert result["analysis_id"] == analysis_id

    assert result["state"] == {
        "status": "running",
        "stage": "analysis",
        "progress": "20",
    }

    assert result["ttl"] > 0

async def test_inspect_analysis_queue():
    queue = get_analysis_queue()

    try:
        await queue.add(
            "test-inspector",
            {
                "repository_path": "./compiler",
            },
        )

        result = await inspect_analysis_queue()

        assert result["queue"] == "analysis"

        counts = result["counts"]

        assert "waiting" in counts
        assert "active" in counts
        assert "completed" in counts
        assert "failed" in counts
        assert "delayed" in counts

        assert all(count >= 0 for count in counts.values())
    finally:
        await queue.close()

def test_inspect_analysis_channel() -> dict:
    redis, pubsub = get_analysis_events()

    try:
        result = inspect_analysis_channel()

        assert result["channel"] == ANALYSIS_CHANNEL
        assert result["subscribers"] >= 1
    finally:
        pubsub.close()
        redis.close()
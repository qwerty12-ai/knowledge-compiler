from backend.app.services.redis_subscriber import (get_analysis_events, read_analysis_event)
from backend.app.services.redis_state import (publish_analysis_event)


def test_read_analysis_event():
    redis, pubsub = get_analysis_events()

    try:
        pubsub.get_message(timeout=1)

        publish_analysis_event(
            analysis_id="test-analysis",
            status="running",
            stage="analysis",
            progress=20,
        )

        event = read_analysis_event(pubsub)

        assert event is not None
        assert event == {
            "analysis_id": "test-analysis",
            "status": "running",
            "stage": "analysis",
            "progress": 20,
        }

    finally:
        pubsub.close()
        redis.close()
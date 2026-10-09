from backend.app.services.redis_state import (
    set_analysis_state,
)
from backend.app.services.redis_subscriber import (
    get_analysis_events,
    read_analysis_event,
    stream_analysis_events,
)


def test_read_analysis_event():
    redis, pubsub = get_analysis_events()

    try:
        set_analysis_state(
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


def test_stream_analysis_events_sends_current_state():
    analysis_id = "test-analysis-stream"

    set_analysis_state(
        analysis_id=analysis_id,
        status="completed",
        stage="completed",
        progress=100,
        database_id=42,
    )

    stream = stream_analysis_events(analysis_id)

    try:
        first_event = next(stream)

        assert first_event.startswith("data: ")

        assert (
            '"analysis_id": "test-analysis-stream"'
            in first_event
        )

        assert '"status": "completed"' in first_event
        assert '"stage": "completed"' in first_event
        assert '"progress": 100' in first_event
        assert '"database_id": 42' in first_event

    finally:
        stream.close()
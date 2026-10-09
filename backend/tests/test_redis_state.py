import json
from backend.app.redis import get_redis_connection
from backend.app.services.redis_state import (set_analysis_state, get_analysis_state, ANALYSIS_STATE_TTL, ANALYSIS_CHANNEL)

def test_set_and_get_analysis_state():
    analysis_id = "test-analysis-1"

    set_analysis_state(
        analysis_id=analysis_id,
        status="running",
        stage="discovery",
        progress=25
    )

    state = get_analysis_state(analysis_id)

    assert state["status"] == "running"
    assert state["stage"] == "discovery"
    assert state["progress"] == "25"

def test_analysis_state_has_ttl():
    analysis_id = "test-analysis-ttl"

    set_analysis_state(
        analysis_id=analysis_id,
        status="running",
        stage="discovery",
        progress=25
    )

    redis = get_redis_connection()
    key=f"analysis:{analysis_id}"

    ttl = redis.ttl(key)

    assert ttl > 0
    assert ttl <= ANALYSIS_STATE_TTL

def test_publish_analysis_event():
    redis = get_redis_connection()
    pubsub = redis.pubsub()

    try:
        pubsub.subscribe(ANALYSIS_CHANNEL)
        pubsub.get_message(timeout=1)

        set_analysis_state(
            analysis_id="test-analysis",
            status="running",
            stage="analysis",
            progress=20
        )

        message = pubsub.get_message(timeout=1)

        assert message is not None
        assert message["type"] == "message"
        assert message["channel"] == ANALYSIS_CHANNEL

        data = json.loads(message["data"])

        assert data == {
            "analysis_id":"test-analysis",
            "status":"running",
            "stage":"analysis",
            "progress":20
        }
    finally:
        pubsub.close()
        redis.close()
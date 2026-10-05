from backend.app.redis import get_redis_connection
import json

ANALYSIS_STATE_TTL = 3600
ANALYSIS_CHANNEL = "analysis-events"

def set_analysis_state(analysis_id: str, status: str, stage: str, progress: int) -> None:
    redis = get_redis_connection()


    key=f"analysis: {analysis_id}"

    redis.hset(
        key,
        mapping={
            "status": status,
            "stage": stage,
            "progress": progress
        }
    )

    redis.expire(key, ANALYSIS_STATE_TTL)

    publish_analysis_event(
        analysis_id=analysis_id,
        status=status,
        stage=stage,
        progress=progress
    )

def get_analysis_state(analysis_id: str) -> dict:
    redis = get_redis_connection()

    key=f"analysis: {analysis_id}"

    return redis.hgetall(key)

def publish_analysis_event(analysis_id: str, status: str, stage: str, progress: int) -> None:
    redis = get_redis_connection()

    redis.publish(
        ANALYSIS_CHANNEL,
        json.dumps({
            "analysis_id": analysis_id,
            "status": status,
            "stage": stage,
            "progress": progress 
        })
    )
import json

from ..redis import get_redis_connection

ANALYSIS_STATE_TTL = 3600
ANALYSIS_CHANNEL = "analysis-events"


def set_analysis_state(
    analysis_id: str,
    status: str,
    stage: str,
    progress: int,
    database_id: int | None = None,
) -> None:
    redis_client = get_redis_connection()

    try:
        key = f"analysis:{analysis_id}"

        mapping = {
            "status": status,
            "stage": stage,
            "progress": progress,
        }

        if database_id is not None:
            mapping["database_id"] = database_id

        redis_client.hset(key, mapping=mapping)
        redis_client.expire(key, ANALYSIS_STATE_TTL)

        redis_client.publish(
            ANALYSIS_CHANNEL,
            json.dumps({
                "analysis_id": analysis_id,
                "status": status,
                "stage": stage,
                "progress": progress,
            }),
        )
    finally:
        redis_client.close()


def get_analysis_state(analysis_id: str) -> dict:
    redis_client = get_redis_connection()

    try:
        key = f"analysis:{analysis_id}"
        return redis_client.hgetall(key)
    finally:
        redis_client.close()
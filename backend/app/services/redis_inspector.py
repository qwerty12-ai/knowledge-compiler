from ..redis import get_redis_connection
from ..queue import get_analysis_queue
from .redis_state import ANALYSIS_CHANNEL

def inspect_analysis_state(analysis_id: str) -> dict:
    redis = get_redis_connection()

    key=f"analysis: {analysis_id}"

    state = redis.hgetall(key)
    ttl = redis.ttl(key)

    return {
        "analysis_id": analysis_id,
        "state": state,
        "ttl": ttl
    }

async def inspect_analysis_queue() -> dict:
    queue = get_analysis_queue()

    try:
        counts = await queue.getJobCounts(
            "waiting",
            "active",
            "completed",
            "failed",
            "delayed"
        )

        return {
            "queue": "analysis",
            "counts": counts
        }
    finally:
        await queue.close()

def inspect_analysis_channel() -> dict:
    redis = get_redis_connection()

    subscribers = redis.pubsub_numsub(ANALYSIS_CHANNEL)

    return {
        "channel": ANALYSIS_CHANNEL,
        "subscribers": subscribers[0][1]
    }
from ..redis import get_redis_connection
from ..queue import get_analysis_queue
from .redis_state import ANALYSIS_CHANNEL


def inspect_analysis_state(analysis_id: str) -> dict:
    redis_client = get_redis_connection()

    try:
        key = f"analysis:{analysis_id}"

        # The Inspector dropdown uses database IDs, while Redis
        # state is keyed by the analysis UUID. Resolve the database
        # ID to its UUID when the state hash is still available.
        if analysis_id.isdigit():
            for candidate_key in redis_client.scan_iter(
                match="analysis:*",
                count=100,
            ):
                candidate_state = redis_client.hgetall(
                    candidate_key
                )

                if (
                    candidate_state.get("database_id")
                    == analysis_id
                ):
                    key = candidate_key
                    break

        state = redis_client.hgetall(key)
        ttl = redis_client.ttl(key)

        resolved_analysis_id = key.removeprefix("analysis:")

        return {
            "analysis_id": resolved_analysis_id,
            "state": state,
            "ttl": ttl,
        }
    finally:
        redis_client.close()


async def inspect_analysis_queue() -> dict:
    queue = get_analysis_queue()

    try:
        counts = await queue.getJobCounts(
            "waiting",
            "active",
            "completed",
            "failed",
            "delayed",
        )

        return {
            "queue": "analysis",
            "counts": counts,
        }
    finally:
        await queue.close()


def inspect_analysis_channel() -> dict:
    redis_client = get_redis_connection()

    try:
        subscribers = redis_client.pubsub_numsub(
            ANALYSIS_CHANNEL
        )

        return {
            "channel": ANALYSIS_CHANNEL,
            "subscribers": subscribers[0][1],
        }
    finally:
        redis_client.close()
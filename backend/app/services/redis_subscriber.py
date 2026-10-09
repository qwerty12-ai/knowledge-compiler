import json
from collections.abc import Iterator

from ..redis import get_redis_connection
from .redis_state import (
    ANALYSIS_CHANNEL,
    get_analysis_state,
)


def get_analysis_events():
    redis = get_redis_connection()
    pubsub = None

    try:
        pubsub = redis.pubsub()
        pubsub.subscribe(ANALYSIS_CHANNEL)
        pubsub.get_message(timeout=1)

        return redis, pubsub

    except BaseException:
        try:
            if pubsub is not None:
                pubsub.close()
        finally:
            redis.close()

        raise


def read_analysis_event(pubsub):
    message = pubsub.get_message(timeout=1)

    if message is None:
        return None

    if message["type"] != "message":
        return None

    return json.loads(message["data"])


def format_sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


def stream_analysis_events(
    analysis_id: str,
) -> Iterator[str]:
    redis, pubsub = get_analysis_events()

    try:
        state = get_analysis_state(analysis_id)

        if state:
            current_state = {
                "analysis_id": analysis_id,
                **state,
            }

            if "progress" in current_state:
                current_state["progress"] = int(
                    current_state["progress"]
                )

            if "database_id" in current_state:
                current_state["database_id"] = int(
                    current_state["database_id"]
                )

            yield format_sse(current_state)

            if current_state.get("status") in {
                "completed",
                "failed",
            }:
                return

        while True:
            event = read_analysis_event(pubsub)

            if event is None:
                yield ": keep-alive\n\n"
                continue

            if event.get("analysis_id") != analysis_id:
                continue

            yield format_sse(event)

            if event.get("status") in {
                "completed",
                "failed",
            }:
                return

    finally:
        pubsub.close()
        redis.close()
import json

from ..redis import get_redis_connection
from .redis_state import ANALYSIS_CHANNEL

def get_analysis_events():
    redis = get_redis_connection()
    pubsub = redis.pubsub()

    pubsub.subscribe(ANALYSIS_CHANNEL)

    return redis, pubsub

def read_analysis_event(pubsub):
    message = pubsub.get_message(timeout=1)

    if message is None:
        return None

    if message["type"] != "message":
        return None

    return json.loads(message["data"])
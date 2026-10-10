import os
from bullmq import Queue

ANALYSIS_QUEUE_NAME = "analysis"

def get_redis_options() -> dict:
    return {
        "host": os.getenv("REDIS_HOST", "127.0.0.1"),
        "port": int(os.getenv("REDIS_PORT", "6379"))
    }

def get_analysis_queue() -> Queue:
    return Queue(ANALYSIS_QUEUE_NAME, {
        "connection": get_redis_options()
    })
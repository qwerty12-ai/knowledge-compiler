import os
import redis
from dotenv import load_dotenv

load_dotenv()

def get_redis_connection() -> redis.Redis:
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "127.0.0.1"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True
    )


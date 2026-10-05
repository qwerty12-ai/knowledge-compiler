from backend.app.redis import get_redis_connection

def test_redis_connection():
    connection = get_redis_connection()
    assert connection.ping() is True
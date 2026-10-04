from backend.app.database import get_database_connection

def test_database_connection():
    connection = get_database_connection()

    try:
        assert connection.is_connected()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result == (1,)
        cursor.close()
    finally:
        connection.close()
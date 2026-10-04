import os
import mysql.connector 
from mysql.connector import MySQLConnection
from dotenv import load_dotenv

load_dotenv()

def get_database_connection() -> MySQLConnection:
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        database=os.getenv("MYSQL_DATABASE", "127.0.0.1"),
        user=os.getenv("MYSQL_USER", "knowledge_compiler"),
        password=os.getenv("MYSQL_PASSWORD")
    )
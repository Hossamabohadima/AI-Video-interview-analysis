import psycopg2

DB_CONFIG = {
    "dbname": "interview_ai",
    "user": "postgres",
    "password": "122333",
    "host": "127.0.0.1",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)
import psycopg2

DB_CONFIG = {
    "dbname": "your_db_name",
    "user": "postgres",
    "password": "your_password",
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)
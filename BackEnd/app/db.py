import psycopg2
import psycopg2.extras
from functools import wraps
import asyncio
from concurrent.futures import ThreadPoolExecutor

DB_CONFIG = {
    "dbname": "interview_ai",
    "user": "postgres",
    "password": "122333",#122333/123456789
    "host": "127.0.0.1",
    "port": "5432"
}

_executor = ThreadPoolExecutor(max_workers=5)


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


async def execute_db_query(query: str, params: tuple = ()):
    """Execute a query and return results asynchronously using thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor,
        _execute_query,
        query,
        params
    )


async def execute_db_procedure(procedure: str, params: tuple = ()):
    """Execute a stored procedure asynchronously using thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor,
        _execute_procedure,
        procedure,
        params
    )


def _execute_query(query: str, params: tuple = ()):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(query, params)
        result = cur.fetchall()
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def _execute_procedure(procedure: str, params: tuple = ()):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.callproc(procedure, params)
        result = cur.fetchall()
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
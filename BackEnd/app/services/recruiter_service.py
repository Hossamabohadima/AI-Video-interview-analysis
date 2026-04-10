from db import get_db_connection

def set_threshold_score(user_id: int, score: float):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("CALL set_threshold_score(%s, %s)", (user_id, score))

    conn.commit()
    cur.close()
    conn.close()
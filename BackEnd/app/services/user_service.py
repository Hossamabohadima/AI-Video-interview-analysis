from altair import Dict
from db import get_db_connection

def get_reports(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM get_reports_sp(%s)", (user_id,))
    data = cur.fetchall()

    cur.close()
    conn.close()
    return data


def compare_reports(v1, v2):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM compare_reports_sp(%s, %s)", (v1, v2))
    data = cur.fetchall()

    cur.close()
    conn.close()
    return data


def set_weights(user_id: int, weights: dict[str, float]):
    conn = get_db_connection()
    cur = conn.cursor()

    w = weights

    cur.execute("""
        SELECT set_weights_fn(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        w["SpeechClarity"],
        w["SpeechFluency"],
        w["SpeechConfidence"],
        w["SpeechExpressiveness"],
        w["SpeechEngagement"],
        w["FacialConfidence"],
        w["FacialApproachability"],
        w["FacialEngagement"],
        w["VideoProfessionalism"]
    ))

    result = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return result

def set_threshold_score(user_id: int, score: float):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT set_threshold_score(%s, %s)", (user_id, score))
        success = cur.fetchone()[0]
        conn.commit()
        return success
    except Exception as e:
        conn.rollback()
        print("DB error:", e)
        return False
    finally:
        cur.close()
        conn.close()
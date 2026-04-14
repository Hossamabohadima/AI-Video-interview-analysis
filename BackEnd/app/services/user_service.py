from altair import Dict

from db import get_db_connection

from fastapi import UploadFile
from moviepy import VideoFileClip
import uuid, os, shutil


def _map_user_row(row):
    """Helper to map database row to user dict"""
    if row is None:
        return None
    return {
        "user_id": row[0],
        "name": row[1],
        "role": row[2],
    }


def register_user(payload):
    """
    Register a new user in the system.
    Calls stored procedure register_user to create user record with initial threshold and metric weights.
    """
    from schemas.user import RegistrationRequest
    from db import get_db_connection
    
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "CALL register_user(%s, %s, %s, %s, %s, %s)",
            (
                payload.name,
                payload.email,
                payload.password,
                payload.phone_number,
                payload.role,
                payload.initial_threshold,
            ),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

    return login_user(payload.email, payload.password)


def login_user(email: str, password: str):
    """
    Authenticate user by email and password.
    Returns user information if credentials match, None otherwise.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM login_user_sp(%s, %s)", (email, password))
        row = cur.fetchone()
        return _map_user_row(row)
    finally:
        cur.close()
        conn.close()


def upload_video(file: UploadFile, user_id: int, video_name: str):
    folder = "videos"
    os.makedirs(folder, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    unique_name = video_name + "_" + str(uuid.uuid4()) + ext
    output_path = os.path.join(folder, unique_name)

    duration = 0.0

    try:
        with open(output_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        try:
            with VideoFileClip(output_path) as video:
                duration = video.duration
        except Exception as e:
            print("Error extracting duration:", e)

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT add_video(%s, %s, %s, %s)",
            (unique_name, user_id, duration, "PENDING")
        )

        rec = cur.fetchone()[0]
        conn.commit()

        cur.close()
        conn.close()


        return {
            "video_id": rec["video_id"],
            "file_name": unique_name,
            "duration": duration,
            "status": "DONE"
        }

    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise e


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


def set_weights(user_id: int, weights: Dict[str, float]):
    conn = get_db_connection()
    cur = conn.cursor()

    w = weights

    cur.execute("""
        CALL set_weights_sp(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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

    conn.commit()
    cur.close()
    conn.close()

def set_threshold_score(user_id: int, score: float):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("CALL set_threshold_score(%s, %s)", (user_id, score))

    conn.commit()
    cur.close()
    conn.close()
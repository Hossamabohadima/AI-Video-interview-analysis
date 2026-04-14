from altair import Dict

from db import get_db_connection

from fastapi import UploadFile
from moviepy import VideoFileClip
import uuid, os, shutil



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


def set_weights(user_id: int, weights: dict[str, float]):
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
from db import get_db_connection
from fastapi import UploadFile
from moviepy import VideoFileClip
import uuid, os, shutil
import ffmpeg



def upload_video(file: UploadFile, user_id: int):
    folder = "videos"
    os.makedirs(folder, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
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
            (unique_name, user_id, duration, "DONE")
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
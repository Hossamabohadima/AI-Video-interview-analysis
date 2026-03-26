from db import get_db_connection

def register_user(user):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "CALL register_user(%s, %s, %s, %s, %s, %s)",
        (user.name, user.email, user.password, user.phoneNumber, user.role, user.initial_threshold)
    )

    conn.commit()
    cur.close()
    conn.close()


def login_user(data):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT userid, name, role FROM Users WHERE email=%s AND password=%s",
        (data.email, data.password)
    )

    user = cur.fetchone()

    cur.close()
    conn.close()

    return user


def upload_video(video):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT add_video(%s, %s, %s, %s)",
        (video.video_name, video.user_id, video.duration, video.status)
    )

    video_id = cur.fetchone()[0]
    conn.commit()

    cur.close()
    conn.close()

    return video_id


def get_reports(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT v.videoid, v.videoname, vs.*
        FROM Video v
        LEFT JOIN videoScore vs ON v.videoid = vs.videoid
        WHERE v.userid = %s
    """, (user_id,))

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


def compare_reports(v1, v2):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM videoScore
        WHERE videoid=%s OR videoid=%s
    """, (v1, v2))

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


def set_weights(req):
    conn = get_db_connection()
    cur = conn.cursor()

    w = req.weights

    cur.execute("""
        UPDATE MetricWeight SET
            SpeechClarity=%s,
            SpeechFluency=%s,
            SpeechConfidence=%s,
            SpeechExpressiveness=%s,
            SpeechEngagement=%s,
            FacialConfidence=%s,
            FacialApproachability=%s,
            FacialEngagement=%s,
            VideoProfessionalism=%s
        WHERE userID=%s
    """, (
        w["SpeechClarity"],
        w["SpeechFluency"],
        w["SpeechConfidence"],
        w["SpeechExpressiveness"],
        w["SpeechEngagement"],
        w["FacialConfidence"],
        w["FacialApproachability"],
        w["FacialEngagement"],
        w["VideoProfessionalism"],
        req.user_id
    ))

    conn.commit()
    cur.close()
    conn.close()
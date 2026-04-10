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

    cur.execute("SELECT * FROM login_user_sp(%s, %s)",
                (data.email, data.password))

    user = cur.fetchone()
    print(user)


    cur.close()
    conn.close()
    return user


def set_weights(req):
    conn = get_db_connection()
    cur = conn.cursor()

    w = req.weights

    cur.execute("""
        CALL set_weights_sp(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        req.user_id,
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
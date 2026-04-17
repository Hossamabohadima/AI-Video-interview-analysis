from altair import Dict

from db import get_db_connection
from utils.password_utils import hash_password, verify_password

from fastapi import UploadFile
from moviepy import VideoFileClip
import uuid, os, shutil
from datetime import datetime


def signup_user(name: str, email: str, password: str, phone_number: str, role: str = "USER"):
    """
    Register a new user in the database.
    
    Args:
        name: User's full name
        email: User's email (must be unique)
        password: Plain text password (will be hashed)
        phone_number: User's phone number
        role: User role (USER or RECRUITER)
        
    Returns:
        Dictionary with user_id, name, email, and success message
        
    Raises:
        Exception: If email already exists or database error occurs
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if email already exists
        cur.execute("SELECT userid FROM Users WHERE email = %s", (email,))
        existing_user = cur.fetchone()
        
        if existing_user:
            cur.close()
            conn.close()
            raise Exception("Email already registered")
        
        # Hash the password
        hashed_password = hash_password(password)
        
        # Insert new user
        cur.execute("""
            INSERT INTO Users (name, email, password, phoneNumber, role, createdDate)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING userid, name, email
        """, (name, email, hashed_password, phone_number, role, datetime.now()))
        
        result = cur.fetchone()
        user_id, user_name, user_email = result
        
        conn.commit()
        
        # Initialize threshold and weights for new user
        cur.execute("""
            INSERT INTO Threshold (userID, thresholdValue)
            VALUES (%s, %s)
        """, (user_id, 50.0))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "user_id": user_id,
            "name": user_name,
            "email": user_email,
            "message": "User registered successfully"
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
            cur.close()
            conn.close()
        raise e


def login_user(email: str, password: str):
    """
    Login user with email and password.
    
    Args:
        email: User's email
        password: Plain text password to verify
        
    Returns:
        Dictionary with user_id, name, and email
        
    Raises:
        Exception: If user not found or password incorrect
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Fetch user from database
        cur.execute("""
            SELECT userid, name, email, password 
            FROM Users 
            WHERE email = %s
        """, (email,))
        
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if not result:
            raise Exception("User not found")
        
        user_id, name, user_email, stored_password = result
        
        # Verify password
        if not verify_password(password, stored_password):
            raise Exception("Invalid password")
        
        return {
            "user_id": user_id,
            "name": name,
            "email": user_email,
            "message": "Login successful"
        }
        
    except Exception as e:
        if conn:
            cur.close()
            conn.close()
        raise e



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
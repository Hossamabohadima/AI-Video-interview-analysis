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
        Dictionary with user_id, name, email, role, and success message
        
    Raises:
        ValueError: If validation fails or email already exists
    """
    conn = None
    try:
        # Input validation
        if not name or name.strip() == "":
            raise ValueError("Name cannot be empty")
        
        if not email or email.strip() == "":
            raise ValueError("Email cannot be empty")
        
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Normalize inputs
        name = name.strip()
        email = email.lower().strip()
        role = role.upper() if role else "USER"
        
        # Validate role
        if role not in ["USER", "RECRUITER"]:
            raise ValueError("Role must be either USER or RECRUITER")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if email already exists
        cur.execute("SELECT userid FROM Users WHERE email = %s", (email,))
        existing_user = cur.fetchone()
        
        if existing_user:
            cur.close()
            conn.close()
            raise ValueError("This email is already registered. Please use a different email or try logging in.")
        
        # Hash the password
        try:
            hashed_password = hash_password(password)
        except Exception as e:
            raise ValueError(f"Password hashing failed: {str(e)}")
        
        # Insert new user
        try:
            cur.execute("""
                INSERT INTO Users (name, email, password, phoneNumber, role, createdDate)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING userid, name, email, role
            """, (name, email, hashed_password, phone_number or None, role, datetime.now()))
            
            result = cur.fetchone()
            if not result:
                raise ValueError("Failed to create user record")
            
            user_id, user_name, user_email, user_role = result
            conn.commit()
        except ValueError:
            raise
        except Exception as e:
            conn.rollback()
            raise ValueError(f"Database error during user creation: {str(e)}")
        
        # Initialize threshold for new user
        try:
            cur.execute("""
                INSERT INTO Threshold (userID, thresholdValue)
                VALUES (%s, %s)
            """, (user_id, 50.0))
            conn.commit()
        except Exception as e:
            # Log this but don't fail - threshold can be created later
            print(f"Warning: Failed to initialize threshold for user {user_id}: {str(e)}")
        
        cur.close()
        conn.close()
        
        return {
            "user_id": user_id,
            "name": user_name,
            "email": user_email,
            "role": user_role,
            "message": "Registration successful! You can now log in."
        }
        
    except ValueError:
        if conn:
            conn.rollback()
            conn.close()
        raise  # Re-raise ValueError as-is for validation errors
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        raise ValueError(f"An unexpected error occurred during registration: {str(e)}")


def login_user(email: str, password: str):
    """
    Login user with email and password.
    
    Args:
        email: User's email
        password: Plain text password to verify
        
    Returns:
        Dictionary with user_id, name, email, and role
        
    Raises:
        ValueError: If user not found or password incorrect
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Fetch user from database
        cur.execute("""
            SELECT userid, name, email, password, role 
            FROM Users 
            WHERE email = %s
        """, (email,))
        
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if not result:
            # Generic message for security (don't reveal if email exists)
            raise ValueError("Invalid email or password")
        
        user_id, name, user_email, stored_password, role = result
        
        # Verify password
        if not verify_password(password, stored_password):
            raise ValueError("Invalid email or password")
        
        return {
            "user_id": user_id,
            "name": name,
            "email": user_email,
            "role": role,
            "message": "Login successful"
        }
        
    except ValueError:
        raise  # Re-raise ValueError as-is
    except Exception as e:
        if conn:
            conn.close()
        raise ValueError(f"Login service error: {str(e)}")


def upload_video(file: UploadFile, user_id: int, video_name: str):
    """
    Upload a video file for a user.
    
    Args:
        file: Uploaded video file
        user_id: ID of the user uploading the video
        video_name: Name to assign to the video
        
    Returns:
        Dictionary with video_id, file_name, duration, and status
        
    Raises:
        ValueError: If validation fails or upload fails
    """
    conn = None
    cur = None
    output_path = None
    
    try:
        # Validation
        if not file:
            raise ValueError("No file provided")
        
        if not video_name or video_name.strip() == "":
            raise ValueError("Video name cannot be empty")
        
        if user_id <= 0:
            raise ValueError("Invalid user ID")
        
        # Validate file extension
        allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'}
        _, file_ext = os.path.splitext(file.filename)
        
        if file_ext.lower() not in allowed_extensions:
            raise ValueError(f"Invalid file format. Allowed formats: {', '.join(allowed_extensions)}")
        
        # Create videos directory
        folder = "videos"
        os.makedirs(folder, exist_ok=True)
        
        # Generate unique filename
        ext = os.path.splitext(file.filename)[1]
        unique_name = video_name.strip() + "_" + str(uuid.uuid4()) + ext.lower()
        output_path = os.path.join(folder, unique_name)
        
        # Save file
        try:
            with open(output_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
        except IOError as e:
            raise ValueError(f"Failed to save file: {str(e)}")
        
        # Extract video duration
        duration = 0.0
        try:
            with VideoFileClip(output_path) as video:
                duration = video.duration
        except Exception as e:
            # Log warning but continue - duration can be None
            print(f"Warning: Could not extract duration for {unique_name}: {str(e)}")
            duration = 0.0
        
        # Store in database
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                "SELECT add_video(%s, %s, %s, %s)",
                (unique_name, user_id, duration, "PENDING")
            )
            
            rec = cur.fetchone()
            if not rec:
                raise ValueError("Failed to store video record in database")
            
            video_info = rec[0]
            conn.commit()
            
            # Handle different response formats
            if isinstance(video_info, dict):
                video_id = video_info.get("video_id")
                status = video_info.get("status", "PENDING")
            else:
                # Fallback if function returns different format
                video_id = video_info
                status = "PENDING"
            
            return {
                "video_id": video_id,
                "file_name": unique_name,
                "duration": duration,
                "status": "DONE"
            }
            
        except Exception as e:
            conn.rollback()
            raise ValueError(f"Database error during video upload: {str(e)}")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
        
    except ValueError:
        if output_path and os.path.exists(output_path):
            try:
                os.remove(output_path)
            except Exception as cleanup_error:
                print(f"Failed to cleanup file {output_path}: {str(cleanup_error)}")
        raise  # Re-raise ValueError as-is
    except Exception as e:
        if output_path and os.path.exists(output_path):
            try:
                os.remove(output_path)
            except Exception:
                pass
        raise ValueError(f"Unexpected error during video upload: {str(e)}")


def get_reports(user_id):
    """
    Retrieve all video reports for a user.
    
    Args:
        user_id: ID of the user
        
    Returns:
        List of video reports
        
    Raises:
        ValueError: If user_id invalid or database error occurs
    """
    if user_id <= 0:
        raise ValueError("Invalid user ID")
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM get_reports_sp(%s)", (user_id,))
        data = cur.fetchall()
        
        cur.close()
        conn.close()
        
        if not data:
            return []  # Return empty list if no reports
        
        return data
    except Exception as e:
        if conn:
            conn.close()
        raise ValueError(f"Error retrieving reports: {str(e)}")


def compare_reports(v1, v2):
    """
    Compare video scores between two videos.
    
    Args:
        v1: First video ID
        v2: Second video ID
        
    Returns:
        List of comparison data
        
    Raises:
        ValueError: If video IDs invalid or database error occurs
    """
    if v1 <= 0 or v2 <= 0:
        raise ValueError("Invalid video ID(s)")
    
    if v1 == v2:
        raise ValueError("Cannot compare a video with itself")
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM compare_reports_sp(%s, %s)", (v1, v2))
        data = cur.fetchall()
        
        cur.close()
        conn.close()
        
        if not data:
            raise ValueError("No comparison data found for the specified videos")
        
        return data
    except ValueError:
        if conn:
            conn.close()
        raise
    except Exception as e:
        if conn:
            conn.close()
        raise ValueError(f"Error comparing reports: {str(e)}")


def set_weights(user_id: int, weights: Dict[str, float]):
    """
    Update metric weights for a user.
    
    Args:
        user_id: ID of the user
        weights: Dictionary of metric weights (should sum to 1.0)
        
    Returns:
        Success message
        
    Raises:
        ValueError: If user_id invalid, weights invalid, or database error occurs
    """
    if user_id <= 0:
        raise ValueError("Invalid user ID")
    
    if not weights or not isinstance(weights, dict):
        raise ValueError("Weights must be a non-empty dictionary")
    
    # Validate weight values
    required_keys = [
        "SpeechClarity", "SpeechFluency", "SpeechConfidence",
        "SpeechExpressiveness", "SpeechEngagement", "FacialConfidence",
        "FacialApproachability", "FacialEngagement", "VideoProfessionalism"
    ]
    
    for key in required_keys:
        if key not in weights:
            raise ValueError(f"Missing required weight: {key}")
    
    # Validate each weight is between 0 and 1
    for key, value in weights.items():
        try:
            weight_val = float(value)
            if weight_val < 0 or weight_val > 1:
                raise ValueError(f"Weight {key} must be between 0 and 1, got {weight_val}")
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid weight value for {key}: {str(e)}")
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            CALL set_weights_sp(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            weights.get("SpeechClarity"),
            weights.get("SpeechFluency"),
            weights.get("SpeechConfidence"),
            weights.get("SpeechExpressiveness"),
            weights.get("SpeechEngagement"),
            weights.get("FacialConfidence"),
            weights.get("FacialApproachability"),
            weights.get("FacialEngagement"),
            weights.get("VideoProfessionalism")
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {"message": "Weights updated successfully"}
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        raise ValueError(f"Error updating weights: {str(e)}")


def set_threshold_score(user_id: int, score: float):
    """
    Update threshold score for a user.
    
    Args:
        user_id: ID of the user
        score: Threshold score (0-100)
        
    Returns:
        Success message
        
    Raises:
        ValueError: If user_id invalid, score invalid, or database error occurs
    """
    if user_id <= 0:
        raise ValueError("Invalid user ID")
    
    try:
        score_val = float(score)
        if score_val < 0 or score_val > 100:
            raise ValueError(f"Threshold score must be between 0 and 100, got {score_val}")
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid threshold score: {str(e)}")
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("CALL set_threshold_score(%s, %s)", (user_id, score))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {"message": "Threshold score updated successfully"}
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        raise ValueError(f"Error updating threshold score: {str(e)}")
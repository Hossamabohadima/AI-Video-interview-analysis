from datetime import datetime, timedelta, timezone
import secrets
import hashlib
import psycopg2
import psycopg2.extras
import os
from ..db import get_db_connection
from ..utils.security import hash_password
from ..services.email_service import get_email_service


RESET_TOKEN_EXPIRE_HOURS = 1


def _generate_reset_token() -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(64)


def _hash_token(token: str) -> str:
    """Hash token using SHA-256 for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def _build_reset_link(token: str) -> str:
    """Build the password reset link for the frontend."""
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    return f"{frontend_url}/reset-password?token={token}"

def _send_reset_email(email: str, token: str) -> bool:
    """Send password reset email to user."""
    try:
        # Read email template
            # 1. Resolve path and read file
        template_path = os.path.join(
            os.path.dirname(__file__), "..", "templates", "reset_password_email.html"
        )

        html_template = ""
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                html_template = f.read()
        else:
            # Safe fallback if file isn't found
            html_template = "<h1>Password Reset</h1><p>Link: {{ reset_link }}</p><p>Token: {{ reset_token }}</p>"

        # 2. Build the link
        reset_link = _build_reset_link(token)
        if r"{{ reset_link }}" not in html_template:
              print(r"WARNING: '{{ reset_link }}' placeholder was not found in the HTML file!")
        # 3. Replace placeholders EXACTLY as written in your HTML file
        html_body = html_template.replace(r"{{ reset_link }}", reset_link)
        html_body = html_body.replace(r"{{ reset_token }}", token)
        if r"{{ reset_link }}" in html_body or r"{{ reset_token }}" in html_body:
            print("ERROR: One or more placeholders were NOT replaced!")
        else:
            print("SUCCESS: All placeholders replaced successfully.")
        email_service = get_email_service()
        return email_service.send_email(
            to_email=email,
            subject="🔐 Reset Your InterviewMe Password",
            html_body=html_body,
            text_body=f"""
            Password Reset - InterviewMe
            
            We received a request to reset your password.
            
            Click this link to reset: {reset_link}
            
            Or use this token: {token}
            
            This link expires in 1 hour.
            """
        )
        
    except Exception as e:
        print(f"Failed to send reset email: {e}")
        return False


async def create_password_reset_token(email: str) -> str:
    """Create a password reset token and send email."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cur.execute("SELECT userid, name FROM Users WHERE email = %s", (email,))
        user = cur.fetchone()
        
        if not user:
            print(f"[INFO] Password reset requested for non-existent email: {email}")
            return None
        
        user_id = user["userid"]
        user_name = user.get("name", "User")
        raw_token = _generate_reset_token()
        hashed_token = _hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS)
        
        cur.execute("""
            INSERT INTO password_reset_tokens (user_id, token_hash, expires_at, used)
            VALUES (%s, %s, %s, FALSE)
            ON CONFLICT (user_id) DO UPDATE SET
                token_hash = EXCLUDED.token_hash,
                expires_at = EXCLUDED.expires_at,
                used = FALSE,
                created_at = CURRENT_TIMESTAMP
        """, (user_id, hashed_token, expires_at))
        
        conn.commit()
        
        # Send email
        email_sent = _send_reset_email(email, raw_token)
        
        if email_sent:
            print(f"[INFO] Password reset email sent to {email}")
        else:
            print(f"[WARNING] Failed to send email to {email}. Token: {raw_token}")
        
        return raw_token
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"[DB ERROR] create_password_reset_token: {e}")
        raise ValueError(f"Database error: {str(e)}")
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] create_password_reset_token: {e}")
        raise ValueError(f"Failed to create reset token: {str(e)}")
    finally:
        cur.close()
        conn.close()


async def validate_reset_token(token: str) -> int:
    """Validate a password reset token and return the user_id."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        hashed_token = _hash_token(token)
        
        cur.execute("""
            SELECT user_id, expires_at, used 
            FROM password_reset_tokens 
            WHERE token_hash = %s
        """, (hashed_token,))
        
        record = cur.fetchone()
        
        if not record:
            raise ValueError("Invalid or expired reset token")
        
        if record["used"]:
            raise ValueError("Reset token has already been used")
        
        expires_at = record["expires_at"]
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if expires_at < datetime.now(timezone.utc):
            raise ValueError("Reset token has expired")
        
        return record["user_id"]
        
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to validate reset token: {str(e)}")
    finally:
        cur.close()
        conn.close()


async def reset_password(token: str, new_password: str) -> bool:
    """Reset user password using a valid reset token."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        user_id = await validate_reset_token(token)
        
        hashed_password = hash_password(new_password)
        
        cur.execute(
            "UPDATE Users SET password = %s WHERE userid = %s",
            (hashed_password, user_id)
        )
        
        if cur.rowcount == 0:
            raise ValueError("User not found")
        
        hashed_token = _hash_token(token)
        cur.execute(
            "UPDATE password_reset_tokens SET used = TRUE WHERE token_hash = %s",
            (hashed_token,)
        )
        
        conn.commit()
        return True
        
    except ValueError:
        raise
    except Exception as e:
        conn.rollback()
        raise ValueError(f"Failed to reset password: {str(e)}")
    finally:
        cur.close()
        conn.close()
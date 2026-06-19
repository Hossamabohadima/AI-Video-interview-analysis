import secrets
import hashlib
from datetime import datetime, timezone
import psycopg2
import psycopg2.extras
from ..db import get_db_connection
from ..utils.security import hash_password


RESET_TOKEN_EXPIRE_HOURS = 1


def _generate_reset_token() -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(64)


def _hash_token(token: str) -> str:
    """Hash token using SHA-256 for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()


async def create_password_reset_token(email: str) -> str:
    """Create a password reset token for the given email.

    Returns the raw token (to be sent to user) or None if email not found.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # Check if user exists
        cur.execute("SELECT userid FROM Users WHERE email = %s", (email,))
        user = cur.fetchone()

        if not user:
            return None  # Don't reveal if email exists

        user_id = user["userid"]
        raw_token = _generate_reset_token()
        hashed_token = _hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS)

        # Store token in database
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
        return raw_token

    except Exception as e:
        conn.rollback()
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
        
        # Fix: Handle timezone-naive datetime from PostgreSQL
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
    """Reset user password using a valid reset token.

    Returns True on success, raises ValueError on failure.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Validate token and get user_id
        user_id = await validate_reset_token(token)

        # Hash new password
        hashed_password = hash_password(new_password)

        # Update password
        cur.execute(
            "UPDATE Users SET password = %s WHERE userid = %s",
            (hashed_password, user_id)
        )

        if cur.rowcount == 0:
            raise ValueError("User not found")

        # Mark token as used
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
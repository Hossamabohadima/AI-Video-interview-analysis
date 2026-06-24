from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import os
import bcrypt

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# In-memory token blacklist (use Redis in production)
_token_blacklist = set()


def hash_password(password: str) -> str:
    """Hash password using bcrypt. Truncates to 72 bytes as bcrypt requires."""
    password_bytes = password[:72].encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash using bcrypt."""
    plain_bytes = plain_password[:72].encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


def create_access_token(user_id: int, role: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def blacklist_token(token: str) -> bool:
    """Add a token to the blacklist to prevent reuse after logout."""
    try:
        payload = verify_token(token)
        _token_blacklist.add(token)
        return True
    except Exception:
        return False


def is_token_blacklisted(token: str) -> bool:
    """Check if a token has been blacklisted."""
    return token in _token_blacklist
import hashlib
import secrets


def hash_password(password: str) -> str:
    """
    Hash password using SHA256 with salt for security.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password with salt
    """
    salt = secrets.token_hex(32)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${hashed.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify plain text password against hashed password.
    
    Args:
        password: Plain text password to verify
        hashed_password: Stored hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        salt, hash_value = hashed_password.split('$')
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hashed.hex() == hash_value
    except Exception:
        return False

import psycopg2
import psycopg2.extras
from ..db import get_db_connection, execute_db_query
from ..utils.security import hash_password, verify_password, create_access_token
from ..schemas.user_auth import Registration, LoginRequest, Token, UserResponse


async def register_user(registration: Registration) -> UserResponse:
    """Register a new user using the stored procedure."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Hash the password before storing
        hashed_password = hash_password(registration.password)
        
        # Use CALL for PostgreSQL procedures with hashed password
        cur.execute(
            "CALL register_user(%s, %s, %s, %s, %s, %s)",
            (registration.name, registration.email, hashed_password, 
             registration.phone_number, registration.role, 0.0)
        )
        conn.commit()
        
        # Fetch the newly created user
        cur.execute(
            "SELECT userid, name, email, role, createddate FROM Users WHERE email = %s",
            (registration.email,)
        )
        user = cur.fetchone()
        
        if not user:
            raise ValueError("User registration failed")
        
        return UserResponse(
            user_id=user["userid"],
            name=user["name"],
            email=user["email"],
            role=user["role"],
            created_date=str(user["createddate"])
        )
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if "duplicate key" in str(e).lower():
            raise ValueError("Email already exists")
        raise ValueError("User registration failed")
    except Exception as e:
        conn.rollback()
        raise ValueError(f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()


async def login_user(login_request: LoginRequest) -> Token:
    """Authenticate user and return JWT token."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Use the stored procedure to get user and password hash
        cur.execute(
            "SELECT * FROM login_user_sp(%s, %s)",
            (login_request.email, login_request.password)
        )
        user = cur.fetchone()
        
        if not user:
            raise ValueError("Invalid email or password")
        
        # Verify the password against the hash
        if not verify_password(login_request.password, user["password"]):
            raise ValueError("Invalid email or password")
        
        access_token = create_access_token(user["userid"], user["role"])
        
        return Token(
            access_token=access_token,
            name=user["name"],
            user_id=user["userid"],
            role=user["role"],
        )
    except Exception as e:
        raise ValueError(f"Login failed: {str(e)}")
    finally:
        cur.close()
        conn.close()

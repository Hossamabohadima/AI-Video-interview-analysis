from fastapi import APIRouter, HTTPException, status
from schemas.user import SignUpRequest, SignUpResponse, LoginRequest, LoginResponse
from services.user_service import signup_user, login_user
from utils.jwt_utils import create_access_token
import logging

# Configure logging
logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/signup", response_model=SignUpResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignUpRequest):
    """
    User signup endpoint with JWT token generation.
    
    Args:
        request: SignUpRequest containing name, email, password, phone_number, role
        
    Returns:
        SignUpResponse with user_id, name, email, JWT token, and success message
        
    Raises:
        HTTPException: 
            - 400 Bad Request: Email already exists, invalid input
            - 422 Unprocessable Entity: Validation error
            - 500 Internal Server Error: Database or system error
    """
    try:
        # Validate email format (Pydantic does this automatically, but explicit for clarity)
        if not request.email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email is required"
            )
        
        # Validate password strength (realistic validation)
        if len(request.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must be at least 8 characters"
            )
        
        # Validate name
        if not request.name or request.name.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Name cannot be empty"
            )
        
        # Call service to create user
        result = signup_user(
            name=request.name.strip(),
            email=request.email.lower(),
            password=request.password,
            phone_number=request.phone_number,
            role=request.role.upper() if request.role else "USER"
        )
        
        # Generate JWT token
        token = create_access_token(
            data={"sub": result["user_id"], "role": request.role.upper() or "USER"}
        )
        
        result["token"] = token
        result["message"] = "User registered successfully"
        
        logger.info(f"User {result['user_id']} registered successfully")
        return result
        
    except HTTPException as he:
        logger.warning(f"Signup failed: {he.detail}")
        raise he
    except ValueError as ve:
        logger.warning(f"Validation error during signup: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid input: {str(ve)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration. Please try again later."
        )


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(request: LoginRequest):
    """
    User login endpoint with JWT token generation.
    
    Args:
        request: LoginRequest containing email and password
        
    Returns:
        LoginResponse with user_id, name, email, role, JWT token, and success message
        
    Raises:
        HTTPException:
            - 400 Bad Request: Missing email or password
            - 401 Unauthorized: Invalid credentials (user not found or wrong password)
            - 422 Unprocessable Entity: Validation error
            - 500 Internal Server Error: Database or system error
    """
    try:
        # Validate required fields
        if not request.email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email is required"
            )
        
        if not request.password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password is required"
            )
        
        # Call service to authenticate user
        result = login_user(
            email=request.email.lower(),
            password=request.password
        )
        
        # Generate JWT token
        token = create_access_token(
            data={"sub": result["user_id"], "role": result.get("role", "USER")}
        )
        
        result["token"] = token
        result["message"] = "Login successful"
        
        logger.info(f"User {result['user_id']} logged in successfully")
        return result
        
    except HTTPException as he:
        logger.warning(f"Login failed: {he.detail}")
        raise he
    except ValueError as ve:
        logger.warning(f"Validation error during login: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials: {str(ve)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login. Please try again later."
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for auth service"""
    return {"status": "ok", "service": "auth"}

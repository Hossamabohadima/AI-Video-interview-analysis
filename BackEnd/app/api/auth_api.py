from fastapi import APIRouter, HTTPException, status
from schemas.user import SignUpRequest, SignUpResponse, LoginRequest, LoginResponse
from services.user_service import signup_user, login_user


router = APIRouter()


@router.post("/signup", response_model=SignUpResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignUpRequest):
    """
    User signup endpoint.
    
    Args:
        request: SignUpRequest containing name, email, password, phone_number, role
        
    Returns:
        SignUpResponse with user_id, name, email, and success message
        
    Raises:
        HTTPException: If signup fails (duplicate email, validation error, etc.)
    """
    try:
        result = signup_user(
            name=request.name,
            email=request.email,
            password=request.password,
            phone_number=request.phone_number,
            role=request.role
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(request: LoginRequest):
    """
    User login endpoint.
    
    Args:
        request: LoginRequest containing email and password
        
    Returns:
        LoginResponse with user_id, name, email, and success message
        
    Raises:
        HTTPException: If login fails (user not found or invalid password)
    """
    try:
        result = login_user(
            email=request.email,
            password=request.password
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for auth service"""
    return {"status": "ok", "service": "auth"}

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from ..schemas.user_auth import Registration, LoginRequest, Token, UserResponse
from ..services.user_auth_service import register_user, login_user
from ..utils.security import blacklist_token

router = APIRouter(prefix="/users/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(registration: Registration):
    try:
        user = await register_user(registration)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(login_request: LoginRequest):
    try:
        token = await login_user(login_request)
        return token
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(credentials: HTTPBearer = Depends(security)):
    """Log out the current user by blacklisting their token."""
    try:
        token = credentials.credentials
        success = blacklist_token(token)
        if success:
            return {"message": "Successfully logged out"}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed")
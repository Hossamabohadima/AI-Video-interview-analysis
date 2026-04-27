from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from .security import verify_token

security = HTTPBearer()


async def get_current_user(credentials = Depends(security)) -> dict:
    try:
        payload = verify_token(credentials.credentials)
        user_id = int(payload.get("sub"))
        role = payload.get("role")
        return {"user_id": user_id, "role": role}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_recruiter(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] != "RECRUITER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can access this endpoint"
        )
    return current_user
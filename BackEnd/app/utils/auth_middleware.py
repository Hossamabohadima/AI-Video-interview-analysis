from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from utils.jwt_utils import verify_access_token
from typing import Optional

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    """
    Extract and verify current user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials from request header
        
    Returns:
        Dictionary containing user_id and role
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    token = credentials.credentials
    payload = verify_access_token(token)
    user_id = payload.get("sub")
    role = payload.get("role", "USER")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )
    
    return {"user_id": user_id, "role": role}


async def get_current_user_optional(credentials: Optional[HTTPAuthCredentials] = Depends(security)) -> Optional[dict]:
    """
    Extract current user from JWT token (optional - doesn't fail if missing).
    
    Args:
        credentials: Optional HTTP Bearer credentials from request header
        
    Returns:
        Dictionary with user_id and role, or None if no credentials provided
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = verify_access_token(token)
        user_id = payload.get("sub")
        role = payload.get("role", "USER")
        return {"user_id": user_id, "role": role}
    except HTTPException:
        return None


async def require_role(*allowed_roles: str):
    """
    Factory function to create role-based authorization dependency.
    
    Args:
        allowed_roles: Roles that are allowed to access the endpoint
        
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}",
            )
        
        return current_user
    
    return role_checker

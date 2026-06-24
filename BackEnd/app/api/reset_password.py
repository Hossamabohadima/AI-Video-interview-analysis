from fastapi import APIRouter, HTTPException, status
from ..schemas.reset_password import ForgotPasswordRequest, ResetPasswordRequest, PasswordResetResponse
from ..services.reset_password import create_password_reset_token, reset_password

router = APIRouter(prefix="/users/auth", tags=["authentication"])


@router.post("/forgot-password", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
async def forgot_password(request: ForgotPasswordRequest):
    """Request a password reset link. Email will be sent if account exists."""
    try:
        token = await create_password_reset_token(request.email)
        
        # Reject if email doesn't exist in database
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account found with this email address"
            )
        
        return PasswordResetResponse(
            message="Password reset link has been sent to your email."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )


@router.post("/reset-password", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
async def reset_password_endpoint(request: ResetPasswordRequest):
    """Reset password using a valid reset token."""
    try:
        success = await reset_password(request.token, request.new_password)
        if success:
            return PasswordResetResponse(
                message="Password has been reset successfully. Please log in with your new password."
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while resetting your password"
        )
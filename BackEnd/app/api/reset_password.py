from fastapi import APIRouter, HTTPException, status
import traceback  # Add this
from ..schemas.reset_password import ForgotPasswordRequest, ResetPasswordRequest, PasswordResetResponse
from ..services.reset_password import create_password_reset_token, reset_password

router = APIRouter(prefix="/users/auth", tags=["authentication"])


@router.post("/forgot-password", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
async def forgot_password(request: ForgotPasswordRequest):
    """Request a password reset link."""
    try:
        token = await create_password_reset_token(request.email)
        
        if token:
            print(f"[DEV] Password reset token for {request.email}: {token}")
        
        return PasswordResetResponse(
            message="If an account with that email exists, a password reset link has been sent."
        )
        
    except Exception as e:
        # Log the REAL error
        print(f"[ERROR] forgot_password: {str(e)}")
        traceback.print_exc()  # This prints the full stack trace
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"  # Show real error in response (dev only)
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
        print(f"[ERROR] reset_password: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
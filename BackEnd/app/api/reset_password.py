from fastapi import APIRouter, HTTPException, status
from ..schemas.reset_password import ForgotPasswordRequest, ResetPasswordRequest, PasswordResetResponse
from ..services.reset_password import create_password_reset_token, reset_password

router = APIRouter(prefix="/users/auth", tags=["authentication"])


@router.post("/forgot-password", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
async def forgot_password(request: ForgotPasswordRequest):
    """Request a password reset link.

    Always returns success message to prevent email enumeration attacks.
    In production, this would send an actual email with the reset link.
    """
    try:
        token = await create_password_reset_token(request.email)

        # In production, send email with reset link
        # For development/graduation project, return token in response
        # (This should be replaced with actual email sending)
        if token:
            # Log token for development purposes
            print(f"[DEV] Password reset token for {request.email}: {token}")
            return PasswordResetResponse(
                message="If an account with that email exists, a password reset link has been sent."
            )

        # Always return same message regardless of whether email exists
        return PasswordResetResponse(
            message="If an account with that email exists, a password reset link has been sent."
        )

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
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

UserRole = Literal["USER", "RECRUITER"]


class RegistrationRequest(BaseModel):
    """
    Registration class: Handles user signup data validation.
    Takes user credentials and initial threshold configuration.
    """
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    phone_number: str | None = Field(default=None, max_length=20)
    role: UserRole = "USER"
    initial_threshold: float = Field(default=0.5, ge=0, le=1)


class LoginRequest(BaseModel):
    """Login credentials validation"""
    email: EmailStr
    password: str


class AuthUser(BaseModel):
    """User response model after registration/login"""
    user_id: int
    name: str
    role: UserRole


class RegistrationResponse(BaseModel):
    """Registration response with success message and user data"""
    message: str
    user: AuthUser

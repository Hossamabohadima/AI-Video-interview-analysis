from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class SignUpRequest(BaseModel):
    """Schema for user sign up request"""
    name: str = Field(..., min_length=1, max_length=50, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    phone_number: Optional[str] = Field(None, max_length=20, description="User's phone number")
    role: str = Field(default="USER", description="User role: USER or RECRUITER")


class SignUpResponse(BaseModel):
    """Schema for sign up response"""
    user_id: int
    name: str
    email: str
    token: Optional[str] = None
    message: str


class LoginRequest(BaseModel):
    """Schema for user login request"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class LoginResponse(BaseModel):
    """Schema for login response"""
    user_id: int
    name: str
    email: str
    role: str
    token: str
    message: str

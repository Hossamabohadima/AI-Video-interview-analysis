from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class SignUpRequest(BaseModel):
    """Schema for user sign up request"""
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone_number: Optional[str] = Field(None, max_length=20)
    role: str = Field(default="USER")


class SignUpResponse(BaseModel):
    """Schema for sign up response"""
    user_id: int
    name: str
    email: str
    message: str


class LoginRequest(BaseModel):
    """Schema for user login request"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Schema for login response"""
    user_id: int
    name: str
    email: str
    token: Optional[str] = None

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserRegistration(BaseModel):
    """Schema for user registration with full details"""
    user_id: int
    name: str
    email: str
    phone_number: Optional[str] = None
    role: str
    created_date: datetime


class UserRegistrationCreate(BaseModel):
    """Schema for creating a new user registration"""
    name: str = Field(..., min_length=1, max_length=50)
    email: str
    password: str = Field(..., min_length=8)
    phone_number: Optional[str] = Field(None, max_length=20)
    role: str = Field(default="USER")

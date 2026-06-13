from pydantic import BaseModel, EmailStr, Field


class Registration(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone_number: str = Field(default=None, max_length=20)
    role: str = Field(default="USER", pattern="^(USER|RECRUITER)$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    name: str


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str
    role: str
    created_date: str

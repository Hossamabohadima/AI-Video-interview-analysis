from pydantic import BaseModel, EmailStr
from typing import Optional

class UserSignUp(BaseModel):
    name: str
    email: EmailStr
    password: str
    phoneNumber: Optional[str] = None
    role: str
    initial_threshold: float = 0.0


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
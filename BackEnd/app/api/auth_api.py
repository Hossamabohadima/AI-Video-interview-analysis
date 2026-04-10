from fastapi import APIRouter, HTTPException
from schemas.user_schema import UserSignUp, LoginRequest
from services.user_service import register_user, login_user


router = APIRouter()

@router.post("/signup")
def signup(user: UserSignUp):
    if user.role not in ['USER', 'RECRUITER']:
        raise HTTPException(status_code=400, detail="Invalid role")

    register_user(user)
    return {"message": "User created"}


@router.post("/login")
def login(data: LoginRequest):
    user = login_user(data)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")


    return {
        "user_id": user[0],
        "name": user[1],
        "role": user[2]
    }

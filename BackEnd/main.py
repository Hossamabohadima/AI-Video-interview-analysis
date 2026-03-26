from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import psycopg2

app = FastAPI()

DB_CONFIG = {
    "dbname": "your_db_name",
    "user": "postgres",
    "password": "your_password",
    "host": "localhost",
    "port": "5432"
}


class UserSignUp(BaseModel):
    name: str
    email: EmailStr
    password: str
    phoneNumber: Optional[str] = None
    role: str
    initial_threshold: float = 0.0


@app.post("/signup")
async def signup(user: UserSignUp):
    if user.role not in ['USER', 'RECRUITER']:
        raise HTTPException(status_code=400, detail="Role must be USER or RECRUITER")

    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute(
            "CALL register_user(%s, %s, %s, %s, %s, %s)",
            (user.name, user.email, user.password, user.phoneNumber, user.role, user.initial_threshold)
        )

        conn.commit()
        return {"message": "User registered and initialized successfully!"}

    except Exception as e:
        if conn: conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if conn:
            cur.close()
            conn.close()


@app.post("/auth/login")
async def login(email: str, password: str):
    conn = get_db_connection()
    cur = conn.cursor()
    # البحث عن المستخدم ومطابقة كلمة السر
    cur.execute("SELECT userid, name, role FROM Users WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()

    if user:
        return {"message": "Login successful", "user_id": user[0], "name": user[1]}
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password")

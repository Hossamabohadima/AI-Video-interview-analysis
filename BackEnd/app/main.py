from fastapi import FastAPI

from api.user import router as user_router

app = FastAPI(title="AI Video Interview Analysis API")

app.include_router(user_router)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.user import router as user_router
from .api.user_auth import router as auth_router
from .api.metrics import router as metrics_router
from .api.scores import router as scores_router
from .api.reset_password import router as password_reset_router

app = FastAPI(
    title="interviewMe",
    docs_url="/interviewMe",
    redoc_url=None
)

# Allow frontend to communicate with backend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router)
app.include_router(password_reset_router)  # Password reset endpoints
app.include_router(metrics_router)
app.include_router(scores_router)
app.include_router(user_router)

@app.on_event("startup")
async def startup_event():
    print("\n" + "★"*40)
    print("  interviewMe BACKEND IS ACTIVE")
    print("  Access Swagger UI: http://127.0.0.1:8000/interviewMe")
    print("★"*40 + "\n")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
from fastapi import FastAPI

from routes.auth_routes import router as auth_router
from routes.video_routes import router as video_router
from routes.report_routes import router as report_router
from routes.weight_routes import router as weight_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(video_router, prefix="/video")
app.include_router(report_router, prefix="/reports")
app.include_router(weight_router, prefix="/weights")
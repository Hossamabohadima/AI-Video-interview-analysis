from fastapi import FastAPI

from api.auth_api import router as auth_router
from api.video_api import router as video_router
from api.report_api import router as report_router
from api.weight_api import router as weight_router
from api.threshold_api import router as threshold_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(video_router, prefix="/video")
app.include_router(report_router, prefix="/reports")
app.include_router(weight_router, prefix="/weights")
app.include_router(threshold_router, prefix="/threshold")
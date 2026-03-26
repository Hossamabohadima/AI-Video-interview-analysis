from fastapi import APIRouter
from models.video_models import VideoUpload
from services.user_service import upload_video

router = APIRouter()

@router.post("/upload")
def upload(video: VideoUpload):
    result = upload_video(video)
    return result
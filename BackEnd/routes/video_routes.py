from fastapi import APIRouter
from models.video_models import VideoUpload
from services.user_service import upload_video

router = APIRouter()

@router.post("/upload")
def upload(video: VideoUpload):
    video_id = upload_video(video)
    return {"video_id": video_id}
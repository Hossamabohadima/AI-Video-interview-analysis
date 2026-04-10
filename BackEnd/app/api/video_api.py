from fastapi import APIRouter, UploadFile, File, Form
from services.video_service import upload_video



router = APIRouter()


@router.post("/upload")
def upload(file: UploadFile = File(...), user_id: int = Form(...)):
    return upload_video(file, user_id)
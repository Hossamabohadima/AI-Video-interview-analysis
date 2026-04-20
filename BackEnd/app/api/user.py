from fastapi import APIRouter, UploadFile, File, Form
from typing import Dict
from schemas.Threshold import Threshold
from services.user_service import (
    get_reports, 
    compare_reports, 
    set_weights, 
    set_threshold_score,
)
from services.video import handle_video_upload


router = APIRouter()

# These will be prefixed by the include_router call in main.py
@router.get("/{user_id}")
def reports(user_id: int):
    return {"reports": get_reports(user_id)}

@router.post("/compare")
def compare(video1: int, video2: int):
    return {"comparison": compare_reports(video1, video2)}

@router.put("/threshold")
def update_threshold(req: Threshold):
    set_threshold_score(req.user_id, req.score)
    return {"message": "Threshold is set"}

@router.post("/uploadVideo")
def upload(file: UploadFile = File(...), user_id: int = Form(...), video_name: str = Form(...)):
    return handle_video_upload(file, user_id, video_name)

@router.put("/weights")
def update_weights(user_id: int, weights: Dict[str, float]):
    set_weights(user_id, weights)
    return {"message": "Weights updated"}
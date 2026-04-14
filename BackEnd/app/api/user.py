from altair import Dict
from fastapi import APIRouter
from BackEnd.app.schemas import Threshold
from services.user_service import get_reports, compare_reports, set_weights
from services.user_service import set_threshold_score
from fastapi import APIRouter, UploadFile, File, Form
from services.user_service import upload_video


router = APIRouter()

@router.get("/reports/{user_id}")
def reports(user_id: int):
    return {"reports": get_reports(user_id)}


@router.post("/reports/compare")
def compare( video1: int,video2: int):
    return {"comparison": compare_reports(video1, video2)}

@router.put("/threshold")
def update_threshold(req: Threshold):
    set_threshold_score(req.user_id, req.score)
    return {"message": "Threshold is set"}


@router.post("/uploadVideo")
def upload(file: UploadFile = File(...), user_id: int = Form(...),video_name: str = Form(...)):
    return upload_video(file, user_id, video_name)



@router.put("/weights")
def update_weights(    user_id: int, weights: Dict[str, float]):
    set_weights(user_id, weights)
    return {"message": "Weights updated"}
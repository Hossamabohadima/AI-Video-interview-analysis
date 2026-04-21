from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Dict
from schemas.Threshold import Threshold
from services.user_service import (
    get_reports,
    compare_reports,
    set_weights,
    set_threshold_score,
    upload_video
)

router = APIRouter()


@router.get("/{user_id}")
def reports(user_id: int):
    data = get_reports(user_id)

    if not data:
        raise HTTPException(status_code=404, detail="User reports not found")

    return {"reports": data}


@router.post("/compare")
def compare(video1: int, video2: int):
    result = compare_reports(video1, video2)
    if len(result) <= 1:
        raise HTTPException(status_code=404, detail="at least one video not found for comparison")
    return {"comparison": result}


@router.put("/threshold")
def update_threshold(req: Threshold):
    success = set_threshold_score(req.user_id, req.score)
    print(success)
    if not success:
        raise HTTPException(status_code=400, detail="user not found")
    return {"message": "Threshold is set"}


@router.post("/uploadVideo")
def upload(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    video_name: str = Form(...)
):
    try:
        if not file:
            raise HTTPException(status_code=400, detail="File is required")

        result = upload_video(file, user_id, video_name)
        if not result:
            raise HTTPException(status_code=400, detail="Video upload failed")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/weights")
def update_weights(user_id: int, weights: Dict[str, float]):
    if not weights:
        raise HTTPException(status_code=400, detail="Weights cannot be empty")

    success = set_weights(user_id, weights)
    if not success:
        raise HTTPException(status_code=400, detail="user not found")

    return {"message": "Weights updated"}



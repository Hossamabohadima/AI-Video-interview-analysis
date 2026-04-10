from fastapi import APIRouter
from schemas.video_schema import CompareRequest
from services.video_service import get_reports, compare_reports

router = APIRouter()

@router.get("/{user_id}")
def reports(user_id: int):
    return {"reports": get_reports(user_id)}


@router.post("/compare")
def compare(req: CompareRequest):
    return {"comparison": compare_reports(req.video1, req.video2)}
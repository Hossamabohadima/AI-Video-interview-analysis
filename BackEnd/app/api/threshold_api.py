from fastapi import APIRouter
from schemas.recruiter_schema import RecruiterSetThreshold
from services.recruiter_service import set_threshold_score

router = APIRouter()

@router.put("/")
def update_threshold(req: RecruiterSetThreshold):
    set_threshold_score(req.user_id, req.score)
    return {"message": "Threshold is set"}
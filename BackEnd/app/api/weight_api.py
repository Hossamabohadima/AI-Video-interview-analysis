from fastapi import APIRouter
from schemas.video_schema import WeightUpdate
from services.user_service import set_weights

router = APIRouter()

@router.put("/")
def update_weights(req: WeightUpdate):
    set_weights(req)
    return {"message": "Weights updated"}
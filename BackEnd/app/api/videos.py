from fastapi import APIRouter, HTTPException
from ..services.video import get_scores, process_video
from ..schemas.video import Scores, MetricWeights

router = APIRouter()

@router.get("/videos/{video_id}/scores", response_model=Scores)
def get_video_scores(video_id: int):
    scores = get_scores(video_id)
    if scores is None:
        raise HTTPException(status_code=404, detail="Scores not found for this video")
    return scores

# @router.post("/videos/{video_id}/process", response_model=Scores)
# def process_video_endpoint(video_id: int, weights: MetricWeights):
#     scores = process_video(video_id, weights)
#     if scores is None:
#         raise HTTPException(status_code=404, detail="Video processing failed")
#     return scores
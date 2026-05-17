from fastapi import APIRouter, HTTPException, status, Depends
from schemas.video import Scores
from services.scores_service import get_video_scores
from utils.dependencies import get_current_user

router = APIRouter(prefix="/videos", tags=["videos"], deprecated=True)


@router.get("/{video_id}/scores", response_model=Scores, deprecated=True)
async def get_video_scores_legacy(video_id: int, current_user: dict = Depends(get_current_user)):
    """[DEPRECATED] Use /scores/{video_id} instead."""
    try:
        scores = await get_video_scores(video_id)
        return scores
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
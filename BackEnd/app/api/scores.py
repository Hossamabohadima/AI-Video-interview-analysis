from fastapi import APIRouter, HTTPException, status, Depends
from ..services.scores_service import get_video_scores
from ..utils.dependencies import get_current_user

router = APIRouter(prefix="/scores", tags=["scores"])


@router.get("/{video_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_scores(video_id: int, current_user: dict = Depends(get_current_user)):
    """Retrieve scores for a specific video."""
    try:
        res = await get_video_scores(video_id, current_user["user_id"])
        
        return res
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve scores"
        )

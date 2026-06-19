from fastapi import APIRouter, HTTPException, status, Depends
from ..schemas.video import MetricWeights
from ..services.weights_service import get_metric_weights, set_metric_weights
from ..utils.dependencies import get_current_user

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/weights", response_model=MetricWeights)
async def get_weights(current_user: dict = Depends(get_current_user)):
    """Get current user's metric weights."""
    try:
        weights = await get_metric_weights(current_user["user_id"])
        return weights
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve metric weights"
        )


@router.put("/weights", response_model=dict)
async def update_weights(
    weights: MetricWeights,
    current_user: dict = Depends(get_current_user)
):
    """Update current user's metric weights."""
    try:
        success = await set_metric_weights(current_user["user_id"], weights)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "Metric weights updated successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update metric weights"
        )
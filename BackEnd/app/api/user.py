from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from ..schemas.Threshold import Threshold
from decimal import Decimal
from ..services.user_service import (
    get_reports, 
    compare_reports, 
    set_weights, 
    set_threshold_score,
)
from ..services.video import handle_uploaded_video
from ..utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/reports", status_code=status.HTTP_200_OK)
async def get_user_reports(current_user: dict = Depends(get_current_user)):
    """Retrieve all video reports for the authenticated user."""
    try:
        data = await get_reports(current_user["user_id"])
        return {"reports": data}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reports"
        )


@router.post("/reports/compare", status_code=status.HTTP_200_OK)
async def compare_user_reports(video1: int, video2: int, current_user: dict = Depends(get_current_user)):
    try:
        result = await compare_reports(video1, video2)
        if len(result) < 2: # Changed from <= 1 for clarity
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="At least one video not found for comparison"
            )
        return {"comparison": result}
    except HTTPException as e:
        # Re-raise HTTPExceptions so we see the actual 404 or 500 detail
        raise e
    except Exception as e:
        # Log the real error to your terminal!
        print(f"CRITICAL ERROR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}"
        )

@router.put("/threshold", status_code=status.HTTP_200_OK)
async def update_user_threshold(score: float, current_user: dict = Depends(get_current_user)):
    """Update threshold score for the authenticated user."""
    try:
        success = await set_threshold_score(current_user["user_id"], score)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "Threshold updated successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update threshold"
        )


@router.post("/videos/upload", status_code=status.HTTP_201_CREATED)
async def upload_video(
    file: UploadFile = File(...),
    video_name: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload and process a video for analysis."""
    try:
        result = await handle_uploaded_video(file, current_user["user_id"], video_name)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process video"
        )


@router.put("/weights-legacy", status_code=status.HTTP_200_OK, deprecated=True)
async def update_weights_legacy(weights: dict, current_user: dict = Depends(get_current_user)):
    """[DEPRECATED] Update metric weights. Use /metrics/weights instead."""
    if not weights:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Weights cannot be empty"
        )
    
    try:
        success = await set_weights(current_user["user_id"], weights)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "Weights updated successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update weights"
        )

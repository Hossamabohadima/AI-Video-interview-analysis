from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from ..schemas.Threshold import Threshold
from ..schemas.video import MetricWeights, VideoComparisonRequest
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
async def compare_user_reports(request: VideoComparisonRequest, current_user: dict = Depends(get_current_user)):
    try:
        result = await compare_reports(request.video_ids, current_user["user_id"])
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
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
async def upload_videos(
    files: list[UploadFile] = File(...),
    video_names: list[str] = Form(...),
    fillers_weight: float = Form(...),
    pause_rate_weight: float = Form(...),
    emotion_weight: float = Form(...),
    energy_weight: float = Form(...),
    eye_contact_weight: float = Form(...),
    grammar_weight: float = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload and process multiple videos with metric weights."""
    if len(files) != len(video_names):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The number of files must match the number of video names"
        )

    weights = MetricWeights(
        fillers_weight=fillers_weight,
        pause_rate_weight=pause_rate_weight,
        emotion_weight=emotion_weight,
        energy_weight=energy_weight,
        eye_contact_weight=eye_contact_weight,
        grammar_weight=grammar_weight,
    )

    results = []
    for file, video_name in zip(files, video_names):
        try:
            result = await handle_uploaded_video(file, current_user["user_id"], video_name, weights)
            results.append(result)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process uploaded videos"
            )

    return {"uploaded_videos": results}

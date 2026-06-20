from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends, Body
import json
from ..schemas.video import MetricWeights
from ..services.user_service import (
    get_reports, 
    compare_reports, 
    set_threshold_score,
    get_single_report,
    delete_user_video,
    get_video_processing_status
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve reports: {str(e)}"
        )


@router.get("/reports/{video_id}", status_code=status.HTTP_200_OK)
async def get_user_single_report(
    video_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Retrieve a single cached video report with scores and analysis."""
    try:
        report_data = await get_single_report(video_id, current_user["user_id"])
        return report_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve report: {str(e)}"
        )


@router.post("/reports/compare", status_code=status.HTTP_200_OK)
async def compare_user_reports(
    video_ids: Optional[List[int]] = Body(default=None, embed=True),
    current_user: dict = Depends(get_current_user)
):
    try:
        if video_ids is None or len(video_ids) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide at least two video IDs for comparison"
            )

        result, report = await compare_reports(video_ids, current_user["user_id"])
        print(f"Comparison result: {result}")
        print(f"Generated report: {report}")
        
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except Exception:
                result = {}

        found_ids = set()

        if isinstance(result, dict):
            scores_list = result.get("scores", [])
            if isinstance(scores_list, list):
                found_ids = {
                    row["videoID"]
                    for row in scores_list 
                    if isinstance(row, dict) and "videoID" in row
                }

        requested_ids = list(dict.fromkeys(video_ids))
        missing_ids = [vid for vid in requested_ids if vid not in found_ids]

        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "Some videos not found for comparison",
                    "missing_video_ids": missing_ids
                }
            )
        return {
            "comparison": result, 
            "report": report
        }
        
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update threshold: {str(e)}"
        )


@router.get("/videos/{video_id}/status", status_code=status.HTTP_200_OK)
async def get_video_status(
    video_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get the processing status of a specific video."""
    try:
        status_data = await get_video_processing_status(video_id, current_user["user_id"])
        return status_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve video status: {str(e)}"
        )


@router.delete("/videos/{video_id}", status_code=status.HTTP_200_OK)
async def delete_video(
    video_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a video and all associated data (scores, analysis, files)."""
    try:
        result = await delete_user_video(video_id, current_user["user_id"])
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete video: {str(e)}"
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
                detail=f"Failed to process video '{video_name}': {str(e)}"
            )

    return {"uploaded_videos": results}
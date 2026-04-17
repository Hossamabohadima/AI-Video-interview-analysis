from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from schemas.Threshold import Threshold
from services.user_service import (
    get_reports, compare_reports, set_weights,
    set_threshold_score, upload_video
)
from utils.auth_middleware import get_current_user
from typing import Dict
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/reports/{user_id}")
async def get_user_reports(user_id: int, current_user: dict = Depends(get_current_user)):
    """
    Get all video reports for a user.
    
    Args:
        user_id: ID of the user
        current_user: Current authenticated user
        
    Returns:
        List of user's video reports
        
    Raises:
        HTTPException: 403 if unauthorized, 400 if invalid input, 500 if server error
    """
    try:
        # Authorization: User can only access their own reports
        if current_user["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own reports"
            )
        
        reports = get_reports(user_id)
        logger.info(f"User {user_id} retrieved {len(reports)} reports")
        return {"reports": reports}
        
    except HTTPException:
        raise
    except ValueError as ve:
        logger.warning(f"Validation error retrieving reports for user {user_id}: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error retrieving reports for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reports. Please try again later."
        )


@router.post("/reports/compare")
async def compare_video_reports(
    video1: int,
    video2: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Compare scores between two videos.
    
    Args:
        video1: First video ID
        video2: Second video ID
        current_user: Current authenticated user
        
    Returns:
        Comparison data between the two videos
        
    Raises:
        HTTPException: 400 if invalid input, 401 if unauthorized, 500 if server error
    """
    try:
        # Basic validation
        if video1 <= 0 or video2 <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Video IDs must be positive integers"
            )
        
        # TODO: Add authorization check - verify user owns both videos
        
        comparison = compare_reports(video1, video2)
        logger.info(f"User {current_user['user_id']} compared videos {video1} and {video2}")
        return {"comparison": comparison}
        
    except HTTPException:
        raise
    except ValueError as ve:
        logger.warning(f"Validation error comparing videos {video1} and {video2}: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error comparing videos {video1} and {video2}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compare videos. Please try again later."
        )


@router.put("/threshold")
async def update_user_threshold(
    user_id: int,
    score: float,
    current_user: dict = Depends(get_current_user)
):
    """
    Update threshold score for a user.
    
    Args:
        user_id: ID of the user
        score: New threshold score (0-100)
        current_user: Current authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 403 if unauthorized, 400 if invalid input, 500 if server error
    """
    try:
        # Authorization: User can only update their own threshold
        if current_user["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own threshold"
            )
        
        result = set_threshold_score(user_id, score)
        logger.info(f"User {user_id} updated threshold to {score}")
        return result
        
    except HTTPException:
        raise
    except ValueError as ve:
        logger.warning(f"Validation error updating threshold for user {user_id}: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error updating threshold for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update threshold. Please try again later."
        )


@router.post("/uploadVideo")
async def upload_user_video(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    video_name: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a video for a user.
    
    Args:
        file: Video file to upload
        user_id: ID of the user uploading
        video_name: Name for the video
        current_user: Current authenticated user
        
    Returns:
        Upload details (video_id, file_name, duration, status)
        
    Raises:
        HTTPException: 403 if unauthorized, 400 if invalid input, 500 if server error
    """
    try:
        # Authorization: User can only upload videos for themselves
        if current_user["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only upload videos to your own account"
            )
        
        result = upload_video(file, user_id, video_name)
        logger.info(f"User {user_id} uploaded video: {result['file_name']}")
        return result
        
    except HTTPException:
        raise
    except ValueError as ve:
        logger.warning(f"Validation error uploading video for user {user_id}: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error uploading video for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload video. Please try again later."
        )


@router.put("/weights")
async def update_user_weights(
    user_id: int,
    weights: Dict[str, float],
    current_user: dict = Depends(get_current_user)
):
    """
    Update metric weights for a user.
    
    Args:
        user_id: ID of the user
        weights: Dictionary of metric weights
        current_user: Current authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 403 if unauthorized, 400 if invalid input, 500 if server error
    """
    try:
        # Authorization: User can only update their own weights
        if current_user["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own weights"
            )
        
        result = set_weights(user_id, weights)
        logger.info(f"User {user_id} updated metric weights")
        return result
        
    except HTTPException:
        raise
    except ValueError as ve:
        logger.warning(f"Validation error updating weights for user {user_id}: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error updating weights for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update weights. Please try again later."
        )
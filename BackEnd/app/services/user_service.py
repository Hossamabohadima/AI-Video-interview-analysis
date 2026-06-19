from typing import List
import json
from fastapi import HTTPException
from decimal import Decimal
from openai import AsyncOpenAI
import psycopg2
import psycopg2.extras
from ..db import get_db_connection
from ..schemas.video import MetricWeights
from ..services.report import video_report, compare_between_reports
import os

async def get_reports(user_id: int):
    """Fetch all video reports for a user."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute("SELECT * FROM get_reports_sp(%s)", (user_id,))
        data = cur.fetchall()
        return data if data else []
    except Exception as e:
        raise ValueError(f"Failed to retrieve reports: {str(e)}")
    finally:
        cur.close()
        conn.close()


async def get_single_report(video_id: int, user_id: int) -> dict:
    """Fetch a single cached video report with scores and analysis data.

    Returns the complete report including scores, analysis details, and generated report text.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # Get video info with scores and analysis
        cur.execute(
            "SELECT get_video_score_and_analysis AS data FROM get_video_score_and_analysis(%s, %s)",
            ([video_id], user_id)
        )
        row = cur.fetchone()

        if not row or not row.get("data"):
            raise ValueError(f"Video report not found for video {video_id}")

        result_data = row["data"]
        scores_list = result_data.get("scores", [])
        analysis_list = result_data.get("analysis", [])

        if not scores_list or not analysis_list:
            raise ValueError(f"Incomplete report data for video {video_id}")

        score_data = scores_list[0]
        analysis_data = analysis_list[0]

        # Build complete report response
        return {
            "video_id": video_id,
            "scores": {
                "fillers_score": float(score_data.get("fillers_score", 0)),
                "pause_rate_score": float(score_data.get("pause_rate_score", 0)),
                "emotion_score": float(score_data.get("emotion_score", 0)),
                "energy_score": float(score_data.get("energy_score", 0)),
                "eye_contact_score": float(score_data.get("eye_contact_score", 0)),
                "grammar_score": float(score_data.get("grammar_score", 0)),
                "total_score": float(score_data.get("total_score", 0))
            },
            "analysis": {
                "fillers_words": analysis_data.get("fillers_Word"),
                "rate_of_stop": float(analysis_data.get("rate_Of_Stop", 0)),
                "emotion_analysis": analysis_data.get("emotion_analysis"),
                "energy_statistics": analysis_data.get("energy_Statistics"),
                "eye_contact": analysis_data.get("eye_Contact"),
                "grammar_mistakes": analysis_data.get("grammar_Mistakes")
            }
        }

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to retrieve single report: {str(e)}")
    finally:
        cur.close()
        conn.close()


async def delete_user_video(video_id: int, user_id: int) -> dict:
    """Delete a video and all associated data.

    Deletes:
    - Video file from storage
    - Video record from database (cascades to scores, analysis, weights)
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # First get video info to delete file
        cur.execute(
            "SELECT videoname, userid FROM Video WHERE videoid = %s",
            (video_id,)
        )
        video = cur.fetchone()

        if not video:
            raise ValueError("Video not found")

        if video["userid"] != user_id:
            raise ValueError("Access denied: You can only delete your own videos")

        video_name = video["videoname"]
        video_path = os.path.join("videos", video_name)

        # Delete video file if exists
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
            except OSError as e:
                print(f"Warning: Could not delete video file {video_path}: {e}")

        # Delete from database (cascades to related tables via FK constraints)
        cur.execute("DELETE FROM Video WHERE videoid = %s", (video_id,))
        conn.commit()

        return {
            "message": "Video deleted successfully",
            "video_id": video_id,
            "video_name": video_name
        }

    except ValueError:
        raise
    except Exception as e:
        conn.rollback()
        raise ValueError(f"Failed to delete video: {str(e)}")
    finally:
        cur.close()
        conn.close()


async def compare_reports(video_ids: list[int], user_id: int):
    if len(video_ids) < 2:
        raise ValueError("At least two video IDs are required for comparison")

    conn = get_db_connection()
    cur = conn.cursor()
    print(f"Comparing videos: {video_ids} for user_id: {user_id}")
    try:
        cur.execute(
            "SELECT get_video_score_and_analysis(%s, %s)",
            (video_ids, user_id)
        )
        result = cur.fetchone()[0]

        if isinstance(result, str):
            result = json.loads(result)

        if not result or not result.get("scores"):
            raise HTTPException(
                status_code=404,
                detail="No videos found for comparison"
            )
        Groq_client = AsyncOpenAI(
            api_key="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",
            base_url="https://api.groq.com/openai/v1"
        )
        report = await compare_between_reports(Groq_client, result)
        return result, report
    except HTTPException:
        raise
    except Exception as e:
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to compare reports: {str(e)}")
    finally:
        cur.close()
        conn.close()


async def set_weights(user_id: int, weights: dict):
    """Update metric weights for a user."""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT set_weights_fn(%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            weights["fillers_weight"],
            weights["pause_rate_weight"],
            weights["emotion_weight"],
            weights["energy_weight"],
            weights["eye_contact_weight"],
            weights["grammar_weight"]
        ))

        result = cur.fetchone()[0]
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise ValueError(f"Failed to set weights: {str(e)}")
    finally:
        cur.close()
        conn.close()


async def set_threshold_score(user_id: int, score: float) -> bool:
    """Update threshold score for a user."""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT set_threshold_score(%s, %s)", (user_id, score))
        success = cur.fetchone()[0]
        conn.commit()
        return success
    except psycopg2.IntegrityError:
        conn.rollback()
        raise ValueError("User not found")
    except Exception as e:
        conn.rollback()
        raise ValueError(f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()
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
            SELECT set_weights_fn(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            weights["SpeechClarity"],
            weights["SpeechFluency"],
            weights["SpeechConfidence"],
            weights["SpeechExpressiveness"],
            weights["SpeechEngagement"],
            weights["FacialConfidence"],
            weights["FacialApproachability"],
            weights["FacialEngagement"],
            weights["VideoProfessionalism"]
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
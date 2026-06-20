from openai import AsyncOpenAI
import psycopg2
import psycopg2.extras
import os

from ..services.report import video_report
from ..db import get_db_connection
from ..schemas.video import Scores


def _safe_float(value, default=0.0):
    """Safely convert a value to float, handling None."""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


async def get_video_scores(video_id: int, user_id: int) -> dict:
    """Retrieve scores for a specific video."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cur.execute(
            "SELECT get_video_score_and_analysis AS data FROM get_video_score_and_analysis(%s, %s)",
            ([video_id], user_id)
        )
        row = cur.fetchone()
        
        if not row or not row.get("data"):
            raise ValueError(f"No data returned for video {video_id}")
        
        result_data = row["data"]
        
        scores_list = result_data.get("scores", [])
        analysis_list = result_data.get("analysis", [])
        
        if not scores_list or not analysis_list:
            raise ValueError(f"No scores or analysis found for video {video_id}")
        
        score_data = scores_list[0]
        analysis_data = analysis_list[0]
        
        score = Scores(
            fillers_score=_safe_float(score_data.get("fillers_score"), 0.0),
            pause_rate_score=_safe_float(score_data.get("pause_rate_score"), 0.0),
            emotion_score=_safe_float(score_data.get("emotion_score"), 0.0),
            energy_score=_safe_float(score_data.get("energy_score"), 0.0),
            eye_contact_score=_safe_float(score_data.get("eye_contact_score"), 0.0),
            grammar_score=_safe_float(score_data.get("grammar_score"), 0.0),
            total_score=_safe_float(score_data.get("total_score"), 0.0),
            video_id=video_id
        )
        
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        
        if not GROQ_API_KEY:
            report = "Video analysis completed. LLM report generation unavailable (API key not configured)."
        else:
            groq_client = AsyncOpenAI(
                api_key=GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )
            
            report = await video_report(groq_client, score, {
                "fillers_words": analysis_data.get("fillers_Word") or {},
                "rate_of_stop": _safe_float(analysis_data.get("rate_Of_Stop"), 0.0),
                "emotion_analysis": analysis_data.get("emotion_analysis") or {},
                "energy_statistics": analysis_data.get("energy_Statistics") or {},
                "eye_contact": analysis_data.get("eye_Contact") or {},
                "grammar_mistakes": analysis_data.get("grammar_Mistakes") or [],
            })
        
        return {"score": score, "report": report}
        
    except Exception as e:
        raise ValueError(f"Failed to retrieve scores: {str(e)}")
    finally:
        cur.close()
        conn.close()


async def insert_video_scores(video_id: int, scores: Scores) -> bool:
    """Insert scores for a video using the stored procedure."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.callproc("insert_video_scores", (
            video_id,
            scores.fillers_score,
            scores.pause_rate_score,
            scores.emotion_score,
            scores.energy_score,
            scores.eye_contact_score,
            scores.grammar_score,
            scores.total_score
        ))
        conn.commit()
        return True
    except psycopg2.IntegrityError as e:
        conn.rollback()
        raise ValueError("Video not found or constraint violation")
    except Exception as e:
        conn.rollback()
        raise ValueError(f"Failed to insert scores: {str(e)}")
    finally:
        cur.close()
        conn.close()
from openai import AsyncOpenAI
import psycopg2
import psycopg2.extras

from ..services.report import video_report
from ..db import get_db_connection
from ..schemas.video import Scores


async def get_video_scores(video_id: int, user_id: int) -> dict:
    """Retrieve scores for a specific video."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Note: Keeping the array syntax [video_id] to match your current SQL signature
        cur.execute(
            "SELECT get_video_score_and_analysis AS data FROM get_video_score_and_analysis(%s, %s)",
            ([video_id], user_id)
        )
        row = cur.fetchone()
        
        if not row or not row.get("data"):
            raise ValueError(f"No data returned for video {video_id}")
        result_data = row["data"] # This contains {'scores': [...], 'analysis': [...]}
        
        # Extract lists
        scores_list = result_data.get("scores", [])
        analysis_list = result_data.get("analysis", [])
        print()
        if not scores_list or not analysis_list:
            raise ValueError(f"No scores or analysis found for video {video_id}")
        # Since it returns lists, get the first element
        # (Be aware of case-sensitivity changes in your SQL jsonb_build_object keys!)
        score_data = scores_list[0]  
        analysis_data = analysis_list[0]
        score = Scores(
            fillers_score=float(score_data["fillers_score"]),
            pause_rate_score=float(score_data["pause_rate_score"]),
            emotion_score=float(score_data["emotion_score"]),
            energy_score=float(score_data["energy_score"]),
            eye_contact_score=float(score_data["eye_contact_score"]),
            grammar_score=float(score_data["grammar_score"]),
            total_score=float(score_data["total_score"]),
            video_id=video_id
        )
        # Load the API key securely from environmental variables
        groq_client = AsyncOpenAI(
            api_key="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",
            base_url="https://api.groq.com/openai/v1"
        )
        # Keep an eye on casing: SQL built 'fillers_Word' but you are calling 'fillers_words'
        report = await video_report(groq_client, score, {
            "fillers_words": analysis_data["fillers_Word"],
            "rate_of_stop": analysis_data["rate_Of_Stop"],
            "emotion_analysis": analysis_data["emotion_analysis"],
            "energy_statistics": analysis_data["energy_Statistics"],
            "eye_contact": analysis_data["eye_Contact"],
            "grammar_mistakes": analysis_data["grammar_Mistakes"],
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

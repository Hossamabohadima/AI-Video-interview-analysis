import psycopg2
import psycopg2.extras
from ..db import get_db_connection
from ..schemas.video import Scores


async def get_video_scores(video_id: int) -> Scores:
    """Retrieve scores for a specific video."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cur.execute(
            "SELECT * FROM get_video_scores(%s)",
            (video_id,)
        )
        row = cur.fetchone()
        
        if not row:
            raise ValueError(f"No scores found for video {video_id}")
        
        return Scores(
            speech_clarity=float(row["speechClarity"]),
            speech_fluency=float(row["speechFluency"]),
            speech_confidence=float(row["speechConfidence"]),
            speech_expressiveness=float(row["speechExpressiveness"]),
            speech_engagement=float(row["speechEngagement"]),
            facial_confidence=float(row["facialConfidence"]),
            facial_approachability=float(row["facialApproachability"]),
            facial_engagement=float(row["facialEngagement"]),
            video_professionalism=float(row["videoProfessionalism"]),
            total_score=float(row["totalScore"]),
            video_id=video_id
        )
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
            scores.speech_clarity,
            scores.speech_fluency,
            scores.speech_confidence,
            scores.speech_expressiveness,
            scores.speech_engagement,
            scores.facial_confidence,
            scores.facial_approachability,
            scores.facial_engagement,
            scores.video_professionalism,
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

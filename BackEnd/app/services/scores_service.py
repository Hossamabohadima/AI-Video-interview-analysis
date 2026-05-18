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
            fillers_score=float(row["fillers_score"]),
            pause_rate_score=float(row["pause_rate_score"]),
            emotion_score=float(row["emotion_score"]),
            energy_score=float(row["energy_score"]),
            eye_contact_score=float(row["eye_contact_score"]),
            grammar_score=float(row["grammar_score"]),
            total_score=float(row["total_score"]),
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

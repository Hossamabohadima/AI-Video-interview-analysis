import psycopg2
import psycopg2.extras
from ..db import get_db_connection
from ..schemas.video import MetricWeights


async def get_metric_weights(user_id: int) -> MetricWeights:
    """Retrieve metric weights for a user."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cur.execute(
            "SELECT * FROM MetricWeight WHERE userID = %s",
            (user_id,)
        )
        row = cur.fetchone()
        
        if not row:
            return MetricWeights()
        
        return MetricWeights(
            speech_clarity=float(row["speechclarity"]),
            speech_fluency=float(row["speechfluency"]),
            speech_confidence=float(row["speechconfidence"]),
            speech_expressiveness=float(row["speechexpressiveness"]),
            speech_engagement=float(row["speechengagement"]),
            facial_confidence=float(row["facialconfidence"]),
            facial_approachability=float(row["facialapproachability"]),
            facial_engagement=float(row["facialengagement"]),
            video_professionalism=float(row["videoprofessionalism"])
        )
    except Exception as e:
        raise ValueError(f"Failed to retrieve metric weights: {str(e)}")
    finally:
        cur.close()
        conn.close()


async def set_metric_weights(user_id: int, weights: MetricWeights) -> bool:
    """Update metric weights for a user using the stored function."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Validate that weights sum to approximately 1.0
    total = sum([
        weights.speech_clarity,
        weights.speech_fluency,
        weights.speech_confidence,
        weights.speech_expressiveness,
        weights.speech_engagement,
        weights.facial_confidence,
        weights.facial_approachability,
        weights.facial_engagement,
        weights.video_professionalism
    ])
    
    if abs(total - 1.0) > 0.01:  # Allow small floating point errors
        raise ValueError(f"Weights must sum to 1.0, but sum to {total}")
    
    try:
        cur.execute(
            "SELECT set_weights_fn(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                user_id,
                weights.speech_clarity,
                weights.speech_fluency,
                weights.speech_confidence,
                weights.speech_expressiveness,
                weights.speech_engagement,
                weights.facial_confidence,
                weights.facial_approachability,
                weights.facial_engagement,
                weights.video_professionalism
            )
        )
        
        result = cur.fetchone()[0]
        conn.commit()
        
        return result
    except psycopg2.IntegrityError as e:
        conn.rollback()
        raise ValueError("User not found or constraint violation")
    except Exception as e:
        conn.rollback()
        raise ValueError(f"Failed to set metric weights: {str(e)}")
    finally:
        cur.close()
        conn.close()

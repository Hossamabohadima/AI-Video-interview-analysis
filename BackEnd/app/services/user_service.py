from fastapi import HTTPException
from decimal import Decimal
import psycopg2
import psycopg2.extras
from ..db import get_db_connection

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


async def compare_reports(v1: int, v2: int):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    print("dfdff")
    try:
        cur.execute("SELECT * FROM compare_reports_sp(%s, %s)", (v1, v2))
        data = cur.fetchall()
        print(f"Raw comparison data: {data}")  # Debugging line
        # Convert Decimal objects to floats for JSON compatibility
        for row in data:
            for key, value in row.items():
                if isinstance(value, Decimal):
                    row[key] = float(value)
                    
        return data
    except Exception as e:
        # Check your console for the actual error message here
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
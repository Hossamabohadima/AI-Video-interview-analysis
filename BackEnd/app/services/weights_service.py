from ..schemas.video import MetricWeights
from ..db import get_db_connection
import psycopg2


async def get_metric_weights(user_id: int) -> MetricWeights:
    """Fetch user's most recent metric weights from VideoMetricWeight, or return defaults."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get the most recent video's weights for this user
        cur.execute("""
            SELECT vmw.fillers_weight, vmw.pause_rate_weight, vmw.emotion_weight,
                   vmw.energy_weight, vmw.eye_contact_weight, vmw.grammar_weight
            FROM VideoMetricWeight vmw
            JOIN Video v ON vmw.videoID = v.videoID
            WHERE v.userid = %s
            ORDER BY v.uploaddate DESC
            LIMIT 1
        """, (user_id,))
        
        row = cur.fetchone()
        
        if row:
            return MetricWeights(
                fillers_weight=float(row[0]),
                pause_rate_weight=float(row[1]),
                emotion_weight=float(row[2]),
                energy_weight=float(row[3]),
                eye_contact_weight=float(row[4]),
                grammar_weight=float(row[5])
            )
        
        # No videos yet, return defaults
        return MetricWeights()
        
    except Exception as e:
        # If error, return defaults
        return MetricWeights()
    finally:
        cur.close()
        conn.close()


async def set_metric_weights(user_id: int, weights: MetricWeights) -> bool:
    """Save weights by creating a placeholder video entry or updating user's default."""
    total = (
        weights.fillers_weight + weights.pause_rate_weight +
        weights.emotion_weight + weights.energy_weight +
        weights.eye_contact_weight + weights.grammar_weight
    )
    if abs(total - 1.0) > 0.01:
        raise ValueError(f"Weights must sum to 1.0, but sum to {total}")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Option: Store in a "default" video record (videoID = 0 or negative)
        # Or better: create a dedicated user preferences table
        # Since we're using VideoMetricWeight, we'll store as a "template" video
        
        # Check if user has a default weights video entry
        cur.execute("""
            SELECT vmw.videoID 
            FROM VideoMetricWeight vmw
            JOIN Video v ON vmw.videoID = v.videoID
            WHERE v.userid = %s AND v.VideoName = '_default_weights_'
        """, (user_id,))
        
        existing = cur.fetchone()
        
        if existing:
            # Update existing default weights
            video_id = existing[0]
            cur.execute("""
                UPDATE VideoMetricWeight SET
                    fillers_weight = %s,
                    pause_rate_weight = %s,
                    emotion_weight = %s,
                    energy_weight = %s,
                    eye_contact_weight = %s,
                    grammar_weight = %s
                WHERE videoID = %s
            """, (
                weights.fillers_weight,
                weights.pause_rate_weight,
                weights.emotion_weight,
                weights.energy_weight,
                weights.eye_contact_weight,
                weights.grammar_weight,
                video_id
            ))
        else:
            # Create a placeholder video for storing default weights
            cur.execute("""
                INSERT INTO Video (VideoName, userID, duration, status)
                VALUES ('_default_weights_', %s, 0, 'DONE')
                RETURNING videoID
            """, (user_id,))
            
            video_id = cur.fetchone()[0]
            
            cur.execute("""
                INSERT INTO VideoMetricWeight (
                    videoID, fillers_weight, pause_rate_weight, emotion_weight,
                    energy_weight, eye_contact_weight, grammar_weight
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                video_id,
                weights.fillers_weight,
                weights.pause_rate_weight,
                weights.emotion_weight,
                weights.energy_weight,
                weights.eye_contact_weight,
                weights.grammar_weight
            ))
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        raise ValueError(f"Failed to save weights: {str(e)}")
    finally:
        cur.close()
        conn.close()
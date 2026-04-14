from __future__ import annotations

from ..db import get_db_connection
from ..schemas.video import MetricWeight, Score, VideoRecord


def _empty_score() -> Score:
    return Score(
        speechClarity=0.0,
        speechFluency=0.0,
        speechConfidence=0.0,
        speechExpressiveness=0.0,
        speechEngagement=0.0,
        facialConfidence=0.0,
        facialApproachability=0.0,
        facialEngagement=0.0,
        videoProfessionalism=0.0,
        totalScore=0.0,
    )


def process_video(video_data: VideoRecord, weights: MetricWeight) -> Score:
    # The AI model output is calculated in the notebooks for now.
    # The backend keeps the contract and returns the persisted score row.
    score = get_scores(video_data.videoID)
    return score or _empty_score()

def get_scores(video_id: int) -> Score | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM get_video_scores(%s)", (video_id,))
        row = cursor.fetchone()
        if row:
            return Score(
                speechClarity=row[0],
                speechFluency=row[1],
                speechConfidence=row[2],
                speechExpressiveness=row[3],
                speechEngagement=row[4],
                facialConfidence=row[5],
                facialApproachability=row[6],
                facialEngagement=row[7],
                videoProfessionalism=row[8],
                totalScore=row[9]
            )
        return None
    finally:
        cursor.close()
        conn.close()
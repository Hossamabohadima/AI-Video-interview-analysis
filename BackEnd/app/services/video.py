
from BackEnd.app.schemas.video import MetricWeights, video, Scores 
from BackEnd.app.analysis_models import IAnalysisModel
from db import get_db_connection


def process_video(weights: MetricWeights):

    # standardized_video = standardize_video(video)

    # Analysis models

    # calculate scores based on the analysis results and metric weights

    # return scores
    pass


# why this function if it will call another method already??
# we can just call the IAnalysisModel-VideoStandardizer method directly in the process_video method, right?
# def standardize_video(video: video):
#       return VideoStandardizer.standardize(video)


def add_analysis_model(model: IAnalysisModel):

    # logic?
    
    # return None

    pass

def get_scores(video_id: int) -> Scores | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM get_video_scores(%s)", (video_id,))
        row = cursor.fetchone()
        if row:
            return Scores(
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
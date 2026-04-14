from pydantic import BaseModel

class video(BaseModel):
    videoID: int
    uploadTime: str
    # standardizer: VideoStandardizer
    # analysisModels: list[IAnalysisModel]
    # scores: Scores

class Score(BaseModel):
    """
    Score class: Represents video analysis scores across various dimensions.
    Contains scores for speech, facial, and professionalism metrics.
    """
    speechClarity: float
    speechFluency: float
    speechConfidence: float
    speechExpressiveness: float
    speechEngagement: float
    facialConfidence: float
    facialApproachability: float
    facialEngagement: float
    videoProfessionalism: float
    totalScore: float


class MetricWeight(BaseModel):
    """
    MetricWeight class: Stores weighted values for each evaluation metric.
    Used to customize scoring priority for different evaluation categories.
    """
    speechClarity: float = 0.0
    speechFluency: float = 0.0
    speechConfidence: float = 0.0
    speechExpressiveness: float = 0.0
    speechEngagement: float = 0.0
    facialConfidence: float = 0.0
    facialApproachability: float = 0.0
    facialEngagement: float = 0.0
    videoProfessionalism: float = 0.0


# Backward compatibility aliases
Scores = Score
MetricWeights = MetricWeight

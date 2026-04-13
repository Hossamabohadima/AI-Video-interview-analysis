from pydantic import BaseModel

class video(BaseModel):
    videoID: int
    uploadTime: str
    # standardizer: VideoStandardizer
    # analysisModels: list[IAnalysisModel]
    # scores: Scores

class Scores(BaseModel):
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

class MetricWeights(BaseModel):
    speechClarity: float = 0.0
    speechFluency: float = 0.0
    speechConfidence: float = 0.0
    speechExpressiveness: float = 0.0
    speechEngagement: float = 0.0
    facialConfidence: float = 0.0
    facialApproachability: float = 0.0
    facialEngagement: float = 0.0
    videoProfessionalism: float = 0.0

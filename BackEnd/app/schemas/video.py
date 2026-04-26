from pydantic import BaseModel, Field


class Video(BaseModel):
    video_id: int
    video_name: str
    user_id: int
    upload_date: str
    duration: float
    status: str


class Scores(BaseModel):
    speech_clarity: float = Field(..., ge=0, le=100)
    speech_fluency: float = Field(..., ge=0, le=100)
    speech_confidence: float = Field(..., ge=0, le=100)
    speech_expressiveness: float = Field(..., ge=0, le=100)
    speech_engagement: float = Field(..., ge=0, le=100)
    facial_confidence: float = Field(..., ge=0, le=100)
    facial_approachability: float = Field(..., ge=0, le=100)
    facial_engagement: float = Field(..., ge=0, le=100)
    video_professionalism: float = Field(..., ge=0, le=100)
    total_score: float = Field(..., ge=0, le=100)
    video_id: int


class MetricWeights(BaseModel):
    speech_clarity: float = Field(default=0.0, ge=0, le=1)
    speech_fluency: float = Field(default=0.0, ge=0, le=1)
    speech_confidence: float = Field(default=0.0, ge=0, le=1)
    speech_expressiveness: float = Field(default=0.0, ge=0, le=1)
    speech_engagement: float = Field(default=0.0, ge=0, le=1)
    facial_confidence: float = Field(default=0.0, ge=0, le=1)
    facial_approachability: float = Field(default=0.0, ge=0, le=1)
    facial_engagement: float = Field(default=0.0, ge=0, le=1)
    video_professionalism: float = Field(default=0.0, ge=0, le=1)

    class Config:
        json_schema_extra = {
            "example": {
                "speech_clarity": 0.1,
                "speech_fluency": 0.1,
                "speech_confidence": 0.1,
                "speech_expressiveness": 0.1,
                "speech_engagement": 0.1,
                "facial_confidence": 0.1,
                "facial_approachability": 0.1,
                "facial_engagement": 0.1,
                "video_professionalism": 0.1,
            }
        }

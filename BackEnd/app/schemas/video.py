from pydantic import BaseModel, Field

class Video(BaseModel):
    video_id: int = Field(..., gt=0)
    video_name: str = Field(..., min_length=1)
    user_id: int = Field(..., gt=0)
    upload_date: str = Field(..., min_length=1)
    duration: float = Field(..., ge=0)
    status: str = Field(..., min_length=1)

class MetricWeights(BaseModel):
    fillers_weight: float = Field(..., ge=0, le=1)
    pause_rate_weight: float = Field(..., ge=0, le=1)
    emotion_weight: float = Field(..., ge=0, le=1)
    energy_weight: float = Field(..., ge=0, le=1)
    eye_contact_weight: float = Field(..., ge=0, le=1)
    grammar_weight: float = Field(..., ge=0, le=1)

class Scores(BaseModel):
    fillers_score : float = Field(..., ge=0, le=1)
    pause_rate_score : float = Field(..., ge=0, le=1)
    emotion_score : float = Field(..., ge=0, le=1)
    energy_score : float = Field(..., ge=0, le=1)
    eye_contact_score : float = Field(..., ge=0, le=1)
    grammar_score : float = Field(..., ge=0, le=1)
    total_score : float = Field(..., ge=0, le=1)
    video_id: int = Field(..., gt=0)
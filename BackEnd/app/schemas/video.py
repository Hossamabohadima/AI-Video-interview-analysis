from typing import List
from pydantic import BaseModel, Field, model_validator

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

    @model_validator(mode='after')
    def weights_must_sum_to_one(self) -> 'MetricWeights':
        # Sum the values directly from the model attributes
        total = (
            self.fillers_weight
            + self.pause_rate_weight
            + self.emotion_weight
            + self.energy_weight
            + self.eye_contact_weight
            + self.grammar_weight
        )
        
        # Use math.isclose or keep your current delta check
        if abs(total - 1.0) > 1e-6:
            raise ValueError('Metric weights must sum to 1.0')
            
        # Crucial for Pydantic v2: always return self
        return self
class VideoComparisonRequest(BaseModel):
    video_ids: List[int] = Field(..., min_items=2)
class Scores(BaseModel):
    fillers_score : float = Field(..., ge=0, le=1)
    pause_rate_score : float = Field(..., ge=0, le=1)
    emotion_score : float = Field(..., ge=0, le=1)
    energy_score : float = Field(..., ge=0, le=1)
    eye_contact_score : float = Field(..., ge=0, le=1)
    grammar_score : float = Field(..., ge=0, le=1)
    total_score : float = Field(..., ge=0, le=1)
    video_id: int = Field(..., gt=0)
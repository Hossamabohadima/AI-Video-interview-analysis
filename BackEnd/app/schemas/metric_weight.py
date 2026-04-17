from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class MetricWeightCreate(BaseModel):
    """Schema for creating/updating metric weights"""
    user_id: int
    speech_clarity: Decimal = Field(default=0, ge=0, le=1)
    speech_fluency: Decimal = Field(default=0, ge=0, le=1)
    speech_confidence: Decimal = Field(default=0, ge=0, le=1)
    speech_expressiveness: Decimal = Field(default=0, ge=0, le=1)
    speech_engagement: Decimal = Field(default=0, ge=0, le=1)
    facial_confidence: Decimal = Field(default=0, ge=0, le=1)
    facial_approachability: Decimal = Field(default=0, ge=0, le=1)
    facial_engagement: Decimal = Field(default=0, ge=0, le=1)
    video_professionalism: Decimal = Field(default=0, ge=0, le=1)


class MetricWeightResponse(BaseModel):
    """Schema for metric weights response"""
    user_id: int
    speech_clarity: Decimal
    speech_fluency: Decimal
    speech_confidence: Decimal
    speech_expressiveness: Decimal
    speech_engagement: Decimal
    facial_confidence: Decimal
    facial_approachability: Decimal
    facial_engagement: Decimal
    video_professionalism: Decimal


class MetricWeightUpdate(BaseModel):
    """Schema for updating specific metric weights"""
    speech_clarity: Optional[Decimal] = Field(None, ge=0, le=1)
    speech_fluency: Optional[Decimal] = Field(None, ge=0, le=1)
    speech_confidence: Optional[Decimal] = Field(None, ge=0, le=1)
    speech_expressiveness: Optional[Decimal] = Field(None, ge=0, le=1)
    speech_engagement: Optional[Decimal] = Field(None, ge=0, le=1)
    facial_confidence: Optional[Decimal] = Field(None, ge=0, le=1)
    facial_approachability: Optional[Decimal] = Field(None, ge=0, le=1)
    facial_engagement: Optional[Decimal] = Field(None, ge=0, le=1)
    video_professionalism: Optional[Decimal] = Field(None, ge=0, le=1)

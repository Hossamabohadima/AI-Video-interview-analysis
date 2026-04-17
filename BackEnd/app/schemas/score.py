from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class VideoScore(BaseModel):
    """Schema for video scores"""
    video_id: int
    speech_clarity: Decimal = Field(default=0, ge=0, le=100)
    speech_fluency: Decimal = Field(default=0, ge=0, le=100)
    speech_confidence: Decimal = Field(default=0, ge=0, le=100)
    speech_expressiveness: Decimal = Field(default=0, ge=0, le=100)
    speech_engagement: Decimal = Field(default=0, ge=0, le=100)
    facial_confidence: Decimal = Field(default=0, ge=0, le=100)
    facial_approachability: Decimal = Field(default=0, ge=0, le=100)
    facial_engagement: Decimal = Field(default=0, ge=0, le=100)
    video_professionalism: Decimal = Field(default=0, ge=0, le=100)
    total_score: Optional[Decimal] = Field(None, ge=0, le=100)


class VideoScoreCreate(BaseModel):
    """Schema for creating video scores"""
    video_id: int
    speech_clarity: Decimal = Field(ge=0, le=100)
    speech_fluency: Decimal = Field(ge=0, le=100)
    speech_confidence: Decimal = Field(ge=0, le=100)
    speech_expressiveness: Decimal = Field(ge=0, le=100)
    speech_engagement: Decimal = Field(ge=0, le=100)
    facial_confidence: Decimal = Field(ge=0, le=100)
    facial_approachability: Decimal = Field(ge=0, le=100)
    facial_engagement: Decimal = Field(ge=0, le=100)
    video_professionalism: Decimal = Field(ge=0, le=100)
    total_score: Optional[Decimal] = Field(None, ge=0, le=100)


class VideoScoreUpdate(BaseModel):
    """Schema for updating video scores"""
    speech_clarity: Optional[Decimal] = Field(None, ge=0, le=100)
    speech_fluency: Optional[Decimal] = Field(None, ge=0, le=100)
    speech_confidence: Optional[Decimal] = Field(None, ge=0, le=100)
    speech_expressiveness: Optional[Decimal] = Field(None, ge=0, le=100)
    speech_engagement: Optional[Decimal] = Field(None, ge=0, le=100)
    facial_confidence: Optional[Decimal] = Field(None, ge=0, le=100)
    facial_approachability: Optional[Decimal] = Field(None, ge=0, le=100)
    facial_engagement: Optional[Decimal] = Field(None, ge=0, le=100)
    video_professionalism: Optional[Decimal] = Field(None, ge=0, le=100)
    total_score: Optional[Decimal] = Field(None, ge=0, le=100)


class ScoreComparison(BaseModel):
    """Schema for comparing scores between two videos"""
    video1_id: int
    video2_id: int
    video1_scores: VideoScore
    video2_scores: VideoScore
    differences: dict

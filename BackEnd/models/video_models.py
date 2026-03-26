from pydantic import BaseModel
from typing import Dict

class VideoUpload(BaseModel):
    user_id: int
    video_name: str
    duration: float
    status: str


class CompareRequest(BaseModel):
    user_id: int
    video1: int
    video2: int


class WeightUpdate(BaseModel):
    user_id: int
    weights: Dict[str, float]
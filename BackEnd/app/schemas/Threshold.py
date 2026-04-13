from pydantic import BaseModel, Field

class Threshold(BaseModel):
    user_id: int = Field(..., gt=0)
    score: float = Field(..., ge=0, le=1)
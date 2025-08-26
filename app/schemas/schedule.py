from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ContentSchedule(BaseModel):
    id: int
    area_id: int
    topic_title: str
    scheduled_at: datetime
    status: str = Field(description="pending | generating | reviewing | published | failed")
    lock: Optional[str] = None

    class Config:
        from_attributes = True
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ScheduleCreate(BaseModel):
    content_id: int
    scheduled_at: datetime
    action: str = Field(description="generate | publish")


class ContentSchedule(BaseModel):
    id: int
    area_id: int | None = None
    content_id: int | None = None
    topic_title: str | None = None
    scheduled_at: datetime
    status: str = Field(description="pending | generating | reviewing | published | failed")
    lock: Optional[str] = None

    class Config:
        from_attributes = True
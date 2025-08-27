from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Any


class ContentCreate(BaseModel):
    area_id: int
    topic_title: str


class ContentUpdate(BaseModel):
    micro_outline: Optional[List[dict]] = None
    transcript: Optional[List[dict]] = None
    duration_sec: Optional[int] = None
    status: Optional[str] = None
    review_notes: Optional[str] = None
    publish_url: Optional[HttpUrl] = None


class ContentItem(BaseModel):
    id: int
    area_id: int
    topic_title: str
    micro_outline: Optional[List[dict]] = None
    transcript: Optional[List[dict]] = None
    duration_sec: Optional[int] = None
    status: str
    review_notes: Optional[str] = None
    publish_url: Optional[HttpUrl] = None

    class Config:
        from_attributes = True
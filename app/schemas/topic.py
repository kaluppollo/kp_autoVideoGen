from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional


class TopicIdea(BaseModel):
    title: str
    uniqueness_score: float = Field(ge=0, le=1, description="Stima novità 0-1")


class MicroTopic(BaseModel):
    title: str
    order: int


class GeneratedSection(BaseModel):
    order: int
    text: str
    sources: List[HttpUrl] = []


class TopicContent(BaseModel):
    area_id: int
    topic_title: str
    sections: List[GeneratedSection]
    language: str = "it"
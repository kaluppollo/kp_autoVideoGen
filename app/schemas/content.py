from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Any


class MicroTopic(BaseModel):
    """Schema per un micro-argomento (sezione) del video."""
    order: int = Field(..., description="Ordine della sezione nel video")
    title: str = Field(..., description="Titolo della sezione")
    description: str = Field(..., description="Descrizione del contenuto della sezione")
    estimated_words: int = Field(default=125, description="Numero stimato di parole per questa sezione")
    key_points: List[str] = Field(default_factory=list, description="Punti chiave da trattare nella sezione")


class MicroTopicsRequest(BaseModel):
    """Request per la generazione di micro-argomenti."""
    thematic_area: str = Field(..., description="Area tematica (es. filosofia, psicologia)")
    specific_topic: str = Field(..., description="Argomento specifico del video")
    target_duration_min: int = Field(default=7, ge=3, le=15, description="Durata target del video in minuti")
    words_per_section: int = Field(default=125, ge=80, le=200, description="Numero di parole per sezione")


class MicroTopicsResponse(BaseModel):
    """Response per la generazione di micro-argomenti."""
    success: bool
    micro_topics: List[MicroTopic]
    total_sections: int
    estimated_total_words: int
    estimated_duration_min: float


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
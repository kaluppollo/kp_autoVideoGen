from sqlalchemy import Column, Integer, String, Text, DateTime, func, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SAEnum
import enum

from app.db.models.base import Base


class ContentStatus(str, enum.Enum):
    draft = "draft"
    pending = "pending"
    generating = "generating"
    reviewing = "reviewing"
    ready = "ready"
    published = "published"
    failed = "failed"


class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey("areas.id", ondelete="CASCADE"), nullable=False)

    topic_title = Column(Text, nullable=False)
    micro_outline = Column(JSON, nullable=True)
    transcript = Column(JSON, nullable=True)

    duration_sec = Column(Integer, nullable=True)
    status = Column(SAEnum(ContentStatus, name="content_status", native_enum=False), nullable=False, server_default=ContentStatus.draft.value)
    review_notes = Column(Text, nullable=True)
    publish_url = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    area = relationship("Area", backref="contents")
    media = relationship("Media", backref="content", cascade="all, delete-orphan")
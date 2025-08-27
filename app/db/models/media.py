from sqlalchemy import Column, Integer, String, Text, DateTime, func, JSON, ForeignKey
from sqlalchemy import Enum as SAEnum
import enum

from app.db.models.base import Base


class MediaType(str, enum.Enum):
    image = "image"
    audio = "audio"
    video = "video"
    subtitle = "subtitle"
    cover = "cover"


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey("contents.id", ondelete="CASCADE"), nullable=False)

    type = Column(SAEnum(MediaType, name="media_type", native_enum=False), nullable=False)
    section_order = Column(Integer, nullable=True)
    language = Column(String, nullable=True)
    path = Column(Text, nullable=False)
    # 'metadata' è riservato in SQLAlchemy; usiamo attributo 'meta' con colonna 'metadata'
    meta = Column("metadata", JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
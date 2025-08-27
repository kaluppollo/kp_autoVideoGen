from sqlalchemy import Column, Integer, String, Text, DateTime, func, JSON, ForeignKey
from sqlalchemy import Enum as SAEnum
import enum

from app.db.models.base import Base
from app.db.models.area import SocialPlatform


class PublishStatus(str, enum.Enum):
    pending = "pending"
    uploading = "uploading"
    published = "published"
    failed = "failed"


class PublishQueue(Base):
    __tablename__ = "publish_queue"

    id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey("contents.id", ondelete="CASCADE"), nullable=False)

    target_social = Column(SAEnum(SocialPlatform, name="social_platform", native_enum=False), nullable=False)
    title = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)

    cover_media_id = Column(Integer, ForeignKey("media.id"), nullable=True)
    clip_media_id = Column(Integer, ForeignKey("media.id"), nullable=True)

    status = Column(SAEnum(PublishStatus, name="publish_status", native_enum=False), nullable=False, server_default=PublishStatus.pending.value)
    external_id = Column(String, nullable=True)
    error = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
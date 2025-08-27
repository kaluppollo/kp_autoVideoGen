from sqlalchemy import Column, Integer, Text, DateTime, func, ForeignKey
from sqlalchemy import Enum as SAEnum
import enum

from app.db.models.base import Base


class ScheduleAction(str, enum.Enum):
    generate = "generate"
    publish = "publish"


class ScheduleStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    done = "done"
    skipped = "skipped"
    failed = "failed"


class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey("contents.id", ondelete="CASCADE"), nullable=False)

    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    action = Column(SAEnum(ScheduleAction, name="schedule_action", native_enum=False), nullable=False)
    status = Column(SAEnum(ScheduleStatus, name="schedule_status", native_enum=False), nullable=False, server_default=ScheduleStatus.pending.value)
    lock_token = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
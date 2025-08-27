from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.schedule import Schedule, ScheduleAction, ScheduleStatus


def list_schedules(db: Session):
    return db.execute(select(Schedule)).scalars().all()


def create_schedule(db: Session, content_id: int, scheduled_at: datetime, action: str) -> Schedule:
    if scheduled_at < datetime.utcnow():
        raise ValueError("scheduled_at nel passato non consentito")
    item = Schedule(content_id=content_id, scheduled_at=scheduled_at, action=action)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
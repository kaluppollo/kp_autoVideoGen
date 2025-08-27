from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.schedule import ContentSchedule, ScheduleCreate
from app.services.schedule_service import list_schedules, create_schedule

router = APIRouter()


@router.get("/", response_model=List[ContentSchedule])
def api_list_schedules(db: Session = Depends(get_db)):
    return list_schedules(db)


@router.post("/", response_model=ContentSchedule, status_code=201)
def api_create_schedule(payload: ScheduleCreate, db: Session = Depends(get_db)):
    item = create_schedule(db, payload.content_id, payload.scheduled_at, payload.action)
    return ContentSchedule(
        id=item.id,
        content_id=item.content_id,
        scheduled_at=item.scheduled_at,
        status=item.status.value if hasattr(item.status, 'value') else item.status,
    )
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.thematic_area import ThematicArea, ThematicAreaCreate

router = APIRouter()


@router.get("/", response_model=List[ThematicArea])
def list_thematic_areas(db: Session = Depends(get_db)):
    # TODO: query DB once models are implemented
    return []


@router.post("/", response_model=ThematicArea, status_code=201)
def create_thematic_area(payload: ThematicAreaCreate, db: Session = Depends(get_db)):
    # TODO: persist to DB; for now echo payload with fake ID
    created = ThematicArea(id=1, **payload.model_dump())
    return created
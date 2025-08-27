from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.thematic_area import ThematicArea, ThematicAreaCreate, ThematicAreaUpdate
from app.services.areas_service import list_areas, get_area, create_area, update_area, delete_area

router = APIRouter()


@router.get("/", response_model=List[ThematicArea])
def api_list_areas(db: Session = Depends(get_db)):
    return list_areas(db)


@router.post("/", response_model=ThematicArea, status_code=201)
def api_create_area(payload: ThematicAreaCreate, db: Session = Depends(get_db)):
    item = create_area(
        db,
        name=payload.name,
        primary_social=payload.primary_social,
        logo_url=str(payload.logo_url) if payload.logo_url else None,
        api_keys=payload.api_keys,
    )
    return item


@router.get("/{area_id}", response_model=ThematicArea)
def api_get_area(area_id: int, db: Session = Depends(get_db)):
    item = get_area(db, area_id)
    if not item:
        raise HTTPException(status_code=404, detail="Area non trovata")
    return item


@router.patch("/{area_id}", response_model=ThematicArea)
def api_update_area(area_id: int, payload: ThematicAreaUpdate, db: Session = Depends(get_db)):
    item = get_area(db, area_id)
    if not item:
        raise HTTPException(status_code=404, detail="Area non trovata")
    updated = update_area(db, item, payload.model_dump(exclude_unset=True))
    return updated


@router.delete("/{area_id}", status_code=204)
def api_delete_area(area_id: int, db: Session = Depends(get_db)):
    item = get_area(db, area_id)
    if not item:
        raise HTTPException(status_code=404, detail="Area non trovata")
    delete_area(db, item)
    return None
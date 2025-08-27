from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.area import Area, SocialPlatform


def list_areas(db: Session):
    return db.execute(select(Area)).scalars().all()


def get_area(db: Session, area_id: int) -> Area | None:
    return db.get(Area, area_id)


def create_area(db: Session, name: str, primary_social: str, logo_url: str | None, api_keys: dict | None) -> Area:
    area = Area(
        name=name,
        primary_social=primary_social,
        logo_url=logo_url,
        api_keys=api_keys,
    )
    db.add(area)
    db.commit()
    db.refresh(area)
    return area


def update_area(db: Session, area: Area, data: dict) -> Area:
    for k, v in data.items():
        if v is not None and hasattr(area, k):
            setattr(area, k, v)
    db.add(area)
    db.commit()
    db.refresh(area)
    return area


def delete_area(db: Session, area: Area) -> None:
    db.delete(area)
    db.commit()
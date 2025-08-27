from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.content import Content, ContentStatus


def list_contents(db: Session, area_id: int | None = None):
    stmt = select(Content)
    if area_id is not None:
        stmt = stmt.where(Content.area_id == area_id)
    return db.execute(stmt).scalars().all()


def get_content(db: Session, content_id: int) -> Content | None:
    return db.get(Content, content_id)


def create_content(db: Session, area_id: int, topic_title: str) -> Content:
    content = Content(area_id=area_id, topic_title=topic_title)
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


def update_content(db: Session, content: Content, data: dict) -> Content:
    for k, v in data.items():
        if hasattr(content, k) and v is not None:
            setattr(content, k, v)
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


def exists_topic(db: Session, area_id: int, topic_title: str) -> bool:
    stmt = select(Content).where(Content.area_id == area_id, Content.topic_title == topic_title)
    return db.execute(stmt).scalar_one_or_none() is not None
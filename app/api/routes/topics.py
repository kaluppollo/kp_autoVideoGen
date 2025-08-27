from typing import List
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.contents_service import list_contents, create_content, exists_topic
from app.services.areas_service import get_area
from app.services.topic_generator import generate_topic_ideas
from app.schemas.content import ContentItem

router = APIRouter()


@router.get("/", response_model=List[ContentItem])
def list_topics(area_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    return list_contents(db, area_id=area_id)


@router.post("/generate")
def generate_topics(area_id: int, count: int = 10, db: Session = Depends(get_db)):
    area = get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area non trovata")

    ideas = generate_topic_ideas(area.name, count=count)
    created = []
    for idea in ideas:
        if not exists_topic(db, area_id=area.id, topic_title=idea.title):
            content = create_content(db, area_id=area.id, topic_title=idea.title)
            created.append({"id": content.id, "topic_title": content.topic_title})

    return {"area_id": area.id, "generated": len(created), "items": created}
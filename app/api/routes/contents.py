from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.contents_service import get_content, update_content
from app.services.content_generator import generate_outline
from app.schemas.content import ContentItem


router = APIRouter()


@router.post("/{content_id}/outline", response_model=ContentItem)
def generate_micro_outline(
    content_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """Generate and persist micro-outline (2.1) for a content item.

    Produces 4–8 ordered section titles and saves them into contents.micro_outline.
    """
    content = get_content(db, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content non trovato")

    if content.micro_outline and isinstance(content.micro_outline, list) and len(content.micro_outline) > 0:
        # Idempotent: return existing outline to avoid duplicates
        return content

    outline = generate_outline(content.topic_title)
    content = update_content(db, content, {"micro_outline": outline})
    return content


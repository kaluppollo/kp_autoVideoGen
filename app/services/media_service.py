from typing import Optional, Any
from sqlalchemy.orm import Session

from app.db.models.media import Media, MediaType


def add_media(
    db: Session,
    content_id: int,
    media_type: str,
    path: str,
    section_order: Optional[int] = None,
    language: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> Media:
    item = Media(
        content_id=content_id,
        type=media_type,
        path=path,
        section_order=section_order,
        language=language,
        meta=metadata,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
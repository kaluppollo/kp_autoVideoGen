from typing import Optional
from sqlalchemy.orm import Session

from app.db.models.publish_queue import PublishQueue, PublishStatus


def enqueue_publish(
    db: Session,
    content_id: int,
    target_social: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[list[str]] = None,
    cover_media_id: Optional[int] = None,
    clip_media_id: Optional[int] = None,
) -> PublishQueue:
    item = PublishQueue(
        content_id=content_id,
        target_social=target_social,
        title=title,
        description=description,
        tags=tags,
        cover_media_id=cover_media_id,
        clip_media_id=clip_media_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_publish_status(
    db: Session,
    queue_item: PublishQueue,
    status: str,
    external_id: Optional[str] = None,
    error: Optional[str] = None,
) -> PublishQueue:
    queue_item.status = status
    if external_id is not None:
        queue_item.external_id = external_id
    if error is not None:
        queue_item.error = error
    db.add(queue_item)
    db.commit()
    db.refresh(queue_item)
    return queue_item
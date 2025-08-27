from pathlib import Path
import uuid

from app.core.config import settings


def assemble_video(content_id: int) -> str:
    video_dir = Path(settings.storage_dir) / "video" / str(content_id)
    video_dir.mkdir(parents=True, exist_ok=True)
    fp = video_dir / f"{uuid.uuid4().hex}.mp4"
    fp.write_bytes(b"MP4_PLACEHOLDER")
    return str(fp)
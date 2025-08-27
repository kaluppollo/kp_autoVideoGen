from pathlib import Path
from typing import Dict
import uuid

from app.core.config import settings


def generate_image_for_section(content_id: int, section_order: int, prompt: str) -> str:
    # Placeholder: crea file fittizio
    img_dir = Path(settings.storage_dir) / "img" / str(content_id)
    img_dir.mkdir(parents=True, exist_ok=True)
    fp = img_dir / f"{section_order}_{uuid.uuid4().hex}.png"
    fp.write_bytes(b"PNG_PLACEHOLDER")
    return str(fp)
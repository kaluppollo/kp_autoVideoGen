from pathlib import Path
from typing import List

from app.core.config import settings


def generate_subtitles(content_id: int, languages: List[str] | None = None) -> list[str]:
    if languages is None:
        languages = settings.default_languages
    subs_dir = Path(settings.storage_dir) / "subtitles" / str(content_id)
    subs_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for lang in languages:
        fp = subs_dir / f"{lang}.srt"
        fp.write_text("1\n00:00:00,000 --> 00:00:02,000\nSubtitle placeholder\n")
        files.append(str(fp))
    return files
from pathlib import Path
import uuid

from app.core.config import settings


def synthesize_speech(content_id: int, text: str, language: str = "it") -> str:
    audio_dir = Path(settings.storage_dir) / "audio" / str(content_id)
    audio_dir.mkdir(parents=True, exist_ok=True)
    fp = audio_dir / f"{uuid.uuid4().hex}.wav"
    fp.write_bytes(b"WAV_PLACEHOLDER")
    return str(fp)
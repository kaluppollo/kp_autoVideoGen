from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Centralized application configuration loaded from environment variables.

    This settings object is imported anywhere configuration is needed.
    Interconnections:
    - DB settings are used by app.db.session to create the SQLAlchemy engine
    - API keys and provider names are used by services (image, tts, video)
    - Default languages and durations are used by content/subtitles/video services
    - Scheduler interval is used by scripts/worker_scheduler.py
    """

    app_name: str = Field(default="AutoVideo Studio")
    environment: str = Field(default="development")

    # Database
    database_url: str = Field(default="sqlite:////workspace/db/dev.sqlite3")

    # Providers and API keys (placeholders; choose actual providers later)
    llm_provider: str = Field(default="openai")
    llm_api_key: str | None = None

    image_provider: str = Field(default="stability")  # e.g., stability, midjourney, local
    image_api_key: str | None = None

    tts_provider: str = Field(default="azure")  # e.g., azure, elevenlabs, gcp, local
    tts_api_key: str | None = None

    # Video generation defaults
    default_languages: List[str] = Field(default_factory=lambda: [
        "en",  # English
        "it",  # Italian
        "fr",  # French
        "de",  # German
        "es",  # Spanish
        "hi",  # Hindi
        "zh",  # Chinese (Simplified)
    ])
    default_min_duration_min: int = Field(default=5)
    default_max_duration_min: int = Field(default=10)

    # Scheduling
    scheduler_interval_minutes: int = Field(default=15)

    # Storage
    storage_dir: str = Field(default="/workspace/storage")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
from typing import Optional


def publish_to_social(content_id: int, platform: str, title: str, description: str, video_path: str, cover_path: Optional[str] = None) -> dict:
    # Placeholder: ritorna un id fittizio
    return {"platform": platform, "external_id": f"mock-{content_id}", "url": f"https://{platform}.com/watch?v=mock-{content_id}"}
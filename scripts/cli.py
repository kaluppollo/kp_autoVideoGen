import json
from datetime import datetime, timezone
import time
from typing import Optional

import typer
import uvicorn
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.areas_service import get_area
from app.services.contents_service import create_content, exists_topic, get_content, update_content
from app.services.topic_generator import generate_topic_ideas
from app.services.content_generator import generate_outline, generate_sections
from app.services.image_generator import generate_image_for_section
from app.services.tts_generator import synthesize_speech
from app.services.video_assembler import assemble_video
from app.services.subtitles_generator import generate_subtitles
from app.services.media_service import add_media
from app.services.review_pipeline import run_review
from app.services.publisher import publish_to_social
from app.services.publish_service import enqueue_publish, update_publish_status
from app.db.models.publish_queue import PublishStatus
from app.db.models.media import MediaType
from app.db.models.schedule import Schedule, ScheduleAction, ScheduleStatus
from app.db.models.publish_queue import PublishQueue
from sqlalchemy import select, and_

cli = typer.Typer(help="AutoVideo Studio CLI")


@cli.command()
def serve(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """Avvia l'API FastAPI."""
    uvicorn.run("app.api.main:app", host=host, port=port, reload=reload)


@cli.command("generate-topics")
def generate_topics(area_id: int, count: int = 10):
    """Genera argomenti per un'area e li salva come contenuti draft."""
    db: Session = SessionLocal()
    try:
        area = get_area(db, area_id)
        if not area:
            typer.secho("Area non trovata", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        ideas = generate_topic_ideas(area.name, count=count)
        created = 0
        for idea in ideas:
            if not exists_topic(db, area_id=area.id, topic_title=idea.title):
                create_content(db, area_id=area.id, topic_title=idea.title)
                created += 1
        typer.echo(f"Creati {created} contenuti per area {area.name}")
    finally:
        db.close()


def build_video_for_content(db: Session, content_id: int) -> None:
    content = get_content(db, content_id)
    if not content:
        raise ValueError("Content non trovato")
    outline = generate_outline(content.topic_title)
    sections = generate_sections(outline)
    update_content(db, content, {
        "micro_outline": outline,
        "transcript": sections,
        "status": "generating",
    })

    for section in outline:
        img_path = generate_image_for_section(content.id, section_order=section["order"], prompt=section["title"])
        add_media(db, content_id=content.id, media_type=MediaType.image.value, path=img_path, section_order=section["order"]) 

    for sec in sections:
        audio_path = synthesize_speech(content.id, text=sec["text"], language="it")
        add_media(db, content_id=content.id, media_type=MediaType.audio.value, path=audio_path, section_order=sec["order"], language="it")

    video_path = assemble_video(content.id)
    add_media(db, content_id=content.id, media_type=MediaType.video.value, path=video_path)

    sub_files = generate_subtitles(content.id)
    for sf in sub_files:
        lang = sf.split("/")[-1].split(".")[0]
        add_media(db, content_id=content.id, media_type=MediaType.subtitle.value, path=sf, language=lang)

    update_content(db, content, {"status": "ready"})


@cli.command("build-video")
def build_video(content_id: int):
    """Esegue la pipeline di generazione per un singolo contenuto."""
    db: Session = SessionLocal()
    try:
        build_video_for_content(db, content_id)
        typer.echo(f"Video pronto per content_id={content_id}")
    finally:
        db.close()


@cli.command()
def review(content_id: int):
    """Esegue revisione placeholder per un contenuto."""
    db: Session = SessionLocal()
    try:
        result = run_review(content_id)
        update_content(db, get_content(db, content_id), {"status": "reviewing"})
        if result.get("ok"):
            update_content(db, get_content(db, content_id), {"status": "ready", "review_notes": result.get("notes")})
        typer.echo(json.dumps(result))
    finally:
        db.close()


@cli.command()
def publish(content_id: int, platform: Optional[str] = None):
    """Pubblica un contenuto su una piattaforma (mock)."""
    db: Session = SessionLocal()
    try:
        content = get_content(db, content_id)
        if not content:
            typer.secho("Content non trovato", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        area = content.area
        target = platform or getattr(area, 'primary_social', 'youtube')
        queue_item = enqueue_publish(db, content_id=content.id, target_social=target)
        res = publish_to_social(content.id, target, title=content.topic_title, description="", video_path="")
        update_publish_status(db, queue_item, PublishStatus.published.value, external_id=res.get("external_id"))
        update_content(db, content, {"status": "published", "publish_url": res.get("url")})
        typer.echo(f"Pubblicato su {target}: {res.get('url')}")
    finally:
        db.close()


@cli.command("run-scheduler")
def run_scheduler(loop: bool = True, interval_sec: int = 30):
    """Esegue job pianificati: generate/publish."""
    def run_once(db: Session):
        now = datetime.utcnow()
        q = select(Schedule).where(and_(Schedule.scheduled_at <= now, Schedule.status == ScheduleStatus.pending))
        for sched in db.execute(q).scalars().all():
            if sched.action == ScheduleAction.generate:
                sched.status = ScheduleStatus.running
                db.commit()
                try:
                    build_video_for_content(db, sched.content_id)
                    sched.status = ScheduleStatus.done
                    db.commit()
                except Exception as e:
                    sched.status = ScheduleStatus.failed
                    db.commit()
            elif sched.action == ScheduleAction.publish:
                sched.status = ScheduleStatus.running
                db.commit()
                try:
                    content = get_content(db, sched.content_id)
                    if content:
                        publish(content.id)
                    sched.status = ScheduleStatus.done
                    db.commit()
                except Exception:
                    sched.status = ScheduleStatus.failed
                    db.commit()

    if not loop:
        db: Session = SessionLocal()
        try:
            run_once(db)
        finally:
            db.close()
        return

    typer.echo("Scheduler in esecuzione...")
    while True:
        db: Session = SessionLocal()
        try:
            run_once(db)
        finally:
            db.close()
        time.sleep(interval_sec)


if __name__ == "__main__":
    cli()
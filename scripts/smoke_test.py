import os
import sqlite3
from pathlib import Path
import sys

# Ensure project root on path to import scripts.init_db_sqlite
if '/workspace' not in sys.path:
    sys.path.append('/workspace')

DB_URL = os.environ.get("DATABASE_URL", "sqlite:////workspace/db/dev.sqlite3")
if DB_URL.startswith("sqlite:////"):
    DB_PATH = DB_URL.replace("sqlite:////", "/")
else:
    DB_PATH = DB_URL.replace("sqlite:///", "")

STORAGE_DIR = os.environ.get("STORAGE_DIR", "/workspace/storage")


def run():
    # 1) Ensure schema
    from scripts.init_db_sqlite import schema_sql  # reuse definitions
    # Create schema
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        for stmt in schema_sql:
            cur.executescript(stmt)
        conn.commit()

    # 2) Insert a thematic area
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO areas(name, primary_social) VALUES(?, ?)",
            ("Filosofia", "youtube"),
        )
        conn.commit()
        cur.execute("SELECT id FROM areas WHERE name=?", ("Filosofia",))
        area_id = cur.fetchone()[0]

    # 3) Insert a draft content
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO contents(area_id, topic_title, status) VALUES(?,?,?)",
            (area_id, "Il mito della caverna di Platone", "draft"),
        )
        conn.commit()
        content_id = cur.lastrowid

    # 4) Create placeholder media files in storage
    img_dir = Path(STORAGE_DIR) / "img" / str(content_id)
    audio_dir = Path(STORAGE_DIR) / "audio" / str(content_id)
    video_dir = Path(STORAGE_DIR) / "video" / str(content_id)
    subs_dir = Path(STORAGE_DIR) / "subtitles" / str(content_id)
    for d in (img_dir, audio_dir, video_dir, subs_dir):
        d.mkdir(parents=True, exist_ok=True)

    (img_dir / "1.png").write_bytes(b"PNG_PLACEHOLDER")
    (audio_dir / "it.wav").write_bytes(b"WAV_PLACEHOLDER")
    (video_dir / "final.mp4").write_bytes(b"MP4_PLACEHOLDER")
    (subs_dir / "it.srt").write_text("1\n00:00:00,000 --> 00:00:02,000\nCiao mondo\n")

    # 5) Insert media rows minimally
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO media(content_id, type, section_order, path) VALUES (?,?,?,?)",
            (content_id, "image", 1, str(img_dir / "1.png")),
        )
        cur.execute(
            "INSERT INTO media(content_id, type, language, path) VALUES (?,?,?,?)",
            (content_id, "audio", "it", str(audio_dir / "it.wav")),
        )
        cur.execute(
            "INSERT INTO media(content_id, type, path) VALUES (?,?,?)",
            (content_id, "video", str(video_dir / "final.mp4")),
        )
        cur.execute(
            "INSERT INTO media(content_id, type, language, path) VALUES (?,?,?,?)",
            (content_id, "subtitle", "it", str(subs_dir / "it.srt")),
        )
        conn.commit()

    print("Smoke test OK")
    print("Area ID:", area_id, "Content ID:", content_id)
    print("Storage dirs created under:", STORAGE_DIR)


if __name__ == "__main__":
    run()
import os
import sqlite3
from pathlib import Path

DB_PATH = os.environ.get("DATABASE_URL", "sqlite:////workspace/db/dev.sqlite3")
if DB_PATH.startswith("sqlite:////"):
    SQLITE_FILE = DB_PATH.replace("sqlite:////", "/")
else:
    # Fallback per percorsi tipo sqlite:///relative.db
    SQLITE_FILE = DB_PATH.replace("sqlite:///", "")

Path(os.path.dirname(SQLITE_FILE)).mkdir(parents=True, exist_ok=True)

schema_sql = [
    # areas
    """
    CREATE TABLE IF NOT EXISTS areas (
      id INTEGER PRIMARY KEY,
      name TEXT NOT NULL UNIQUE,
      primary_social TEXT NOT NULL,
      logo_url TEXT,
      api_keys TEXT,
      default_min_duration_min INTEGER NOT NULL DEFAULT 5,
      default_max_duration_min INTEGER NOT NULL DEFAULT 10,
      languages TEXT NOT NULL DEFAULT '["en","it","fr","de","es","hi","zh"]',
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """,
    # contents
    """
    CREATE TABLE IF NOT EXISTS contents (
      id INTEGER PRIMARY KEY,
      area_id INTEGER NOT NULL,
      topic_title TEXT NOT NULL,
      micro_outline TEXT,
      transcript TEXT,
      duration_sec INTEGER,
      status TEXT NOT NULL DEFAULT 'draft',
      review_notes TEXT,
      publish_url TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now')),
      FOREIGN KEY(area_id) REFERENCES areas(id) ON DELETE CASCADE
    );
    """,
    # schedule
    """
    CREATE TABLE IF NOT EXISTS schedule (
      id INTEGER PRIMARY KEY,
      content_id INTEGER NOT NULL,
      scheduled_at TEXT NOT NULL,
      action TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'pending',
      lock_token TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now')),
      FOREIGN KEY(content_id) REFERENCES contents(id) ON DELETE CASCADE
    );
    """,
    # media
    """
    CREATE TABLE IF NOT EXISTS media (
      id INTEGER PRIMARY KEY,
      content_id INTEGER NOT NULL,
      type TEXT NOT NULL,
      section_order INTEGER,
      language TEXT,
      path TEXT NOT NULL,
      metadata TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      FOREIGN KEY(content_id) REFERENCES contents(id) ON DELETE CASCADE
    );
    """,
    # publish_queue
    """
    CREATE TABLE IF NOT EXISTS publish_queue (
      id INTEGER PRIMARY KEY,
      content_id INTEGER NOT NULL,
      target_social TEXT NOT NULL,
      title TEXT,
      description TEXT,
      tags TEXT,
      cover_media_id INTEGER,
      clip_media_id INTEGER,
      status TEXT NOT NULL DEFAULT 'pending',
      external_id TEXT,
      error TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now')),
      FOREIGN KEY(content_id) REFERENCES contents(id) ON DELETE CASCADE,
      FOREIGN KEY(cover_media_id) REFERENCES media(id),
      FOREIGN KEY(clip_media_id) REFERENCES media(id)
    );
    """,
]

with sqlite3.connect(SQLITE_FILE) as conn:
    cur = conn.cursor()
    for stmt in schema_sql:
        cur.executescript(stmt)
    conn.commit()

# Output elenco tabelle
with sqlite3.connect(SQLITE_FILE) as conn:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [r[0] for r in cur.fetchall()]
    print("Created/verified tables:", ", ".join(tables))
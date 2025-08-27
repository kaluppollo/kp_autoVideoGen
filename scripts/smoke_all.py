import os
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Ensure project root on path
if '/workspace' not in sys.path:
    sys.path.append('/workspace')

# Use dedicated smoke DB and storage
os.environ['DATABASE_URL'] = 'sqlite:////workspace/db/smoke.sqlite3'
os.environ['STORAGE_DIR'] = '/workspace/storage/smoke'

# Ensure schema
from scripts.init_db_sqlite import schema_sql
import sqlite3

DB_PATH = '/workspace/db/smoke.sqlite3'
Path('/workspace/db').mkdir(parents=True, exist_ok=True)
with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()
    # Drop existing tables for idempotency
    cur.executescript('''
    PRAGMA foreign_keys=OFF;
    DROP TABLE IF EXISTS publish_queue;
    DROP TABLE IF EXISTS media;
    DROP TABLE IF EXISTS schedule;
    DROP TABLE IF EXISTS contents;
    DROP TABLE IF EXISTS areas;
    PRAGMA foreign_keys=ON;
    ''')
    for stmt in schema_sql:
        cur.executescript(stmt)
    conn.commit()

# API smoke with TestClient
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

# 1) Health
r = client.get('/health/')
assert r.status_code == 200 and r.json().get('status') == 'ok', r.text

# 2) Crea area tematica
payload_area = {
    "name": "Filosofia",
    "primary_social": "youtube",
    "logo_url": None,
    "api_keys": {"openai": "sk-xxx"}
}
r = client.post('/thematic-areas/', json=payload_area)
assert r.status_code == 201, r.text
area = r.json()

# 3) Genera un topic
r = client.post(f"/topics/generate?area_id={area['id']}&count=1")
assert r.status_code == 200, r.text
items = r.json().get('items', [])
assert len(items) >= 1
content_id = items[0]['id']

# 4) Crea schedule per generazione tra 1 secondo
when = (datetime.now(timezone.utc) + timedelta(seconds=1)).isoformat()
r = client.post('/schedules/', json={"content_id": content_id, "scheduled_at": when, "action": "generate"})
assert r.status_code == 201, r.text

print('API smoke OK: area, topic, schedule')

# CLI smoke: build video
import subprocess

env = os.environ.copy()
env['PYTHONPATH'] = '/workspace'
res = subprocess.run([sys.executable, 'scripts/cli.py', 'build-video', str(content_id)], capture_output=True, text=True, cwd='/workspace', env=env)
assert res.returncode == 0, res.stderr or res.stdout
print('CLI build-video OK')

# Verifica media files
storage = Path(os.environ['STORAGE_DIR'])
assert (storage / 'video' / str(content_id)).exists(), 'Video dir missing'
assert (storage / 'subtitles' / str(content_id) / 'it.srt').exists(), 'Subtitle missing'

print('Smoke all OK')
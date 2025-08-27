import os, sys, sqlite3
from pathlib import Path
from datetime import datetime, timedelta, timezone

if '/workspace' not in sys.path:
    sys.path.append('/workspace')

os.environ['DATABASE_URL'] = 'sqlite:////workspace/db/smoke_api.sqlite3'
DB_PATH = '/workspace/db/smoke_api.sqlite3'

from scripts.init_db_sqlite import schema_sql
with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()
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

from fastapi.testclient import TestClient
from app.api.main import app
client = TestClient(app)

assert client.get('/health/').status_code == 200
area = client.post('/thematic-areas/', json={"name":"Test","primary_social":"youtube"}).json()
assert area['id']
resp = client.post(f"/topics/generate?area_id={area['id']}&count=2")
assert resp.status_code == 200
items = resp.json()['items']
assert len(items) >= 1
when = (datetime.now(timezone.utc) + timedelta(seconds=1)).isoformat()
resp = client.post('/schedules/', json={"content_id": items[0]['id'], "scheduled_at": when, "action":"generate"})
assert resp.status_code == 201
print('API smoke OK')
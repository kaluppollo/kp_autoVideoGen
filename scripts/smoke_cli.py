import os, sys, sqlite3
from pathlib import Path

if '/workspace' not in sys.path:
    sys.path.append('/workspace')

os.environ['DATABASE_URL'] = 'sqlite:////workspace/db/smoke_cli.sqlite3'
os.environ['STORAGE_DIR'] = '/workspace/storage/smoke_cli'
DB_PATH = '/workspace/db/smoke_cli.sqlite3'

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

import subprocess

# Create area via Python DB to keep CLI focused on generation
with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()
    cur.execute("INSERT INTO areas(name, primary_social) VALUES(?,?)", ("CLI","youtube"))
    conn.commit()
    area_id = cur.lastrowid

env = os.environ.copy()
env['PYTHONPATH'] = '/workspace'

# Run CLI generate-topics (positional area_id)
res = subprocess.run([sys.executable, 'scripts/cli.py', 'generate-topics', str(area_id), '--count', '2'], capture_output=True, text=True, cwd='/workspace', env=env)
assert res.returncode == 0, res.stderr or res.stdout

# Query contents and build video
with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()
    cur.execute("SELECT id FROM contents WHERE area_id=? ORDER BY id LIMIT 1", (area_id,))
    content_id = cur.fetchone()[0]

# build-video (positional content_id)
res = subprocess.run([sys.executable, 'scripts/cli.py', 'build-video', str(content_id)], capture_output=True, text=True, cwd='/workspace', env=env)
assert res.returncode == 0, res.stderr or res.stdout
print('CLI smoke OK')
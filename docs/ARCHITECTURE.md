# Architettura

Questo documento descrive l'architettura logica del sistema AutoVideo Studio: moduli principali, relazioni, flusso dei dati end‑to‑end e schema del database.

## Moduli principali

1) Topic Management (Gestione Aree e Argomenti)
- Responsabilità: creare e gestire aree tematiche, generare idee di argomenti non duplicati, calendarizzare contenuti.
- Componenti:
  - API `thematic-areas`, `topics`, `schedules`
  - Servizio `services/topic_generator.py` (LLM + deduplica)
  - Scheduler `scripts/worker_scheduler.py` (APScheduler)

2) Generazione Video
- Responsabilità: espandere argomenti in micro-sezioni, generare testo con fonti, immagini per sezione, tracce audio TTS, montare video e creare sottotitoli multilingua.
- Componenti:
  - Servizio contenuti `services/content_generator.py`
  - Servizio immagini `services/image_generator.py`
  - Servizio TTS `services/tts_generator.py`
  - Servizio montaggio video `services/video_assembler.py`
  - Servizio sottotitoli `services/subtitles_generator.py`

3) Revisione (Review)
- Responsabilità: controllo qualità dei contenuti (fact-check, verifica URL, plagio/parafrasi, sincronia audio-sottotitoli-video).
- Componenti:
  - Servizio `services/review_pipeline.py` (LLM critique-pass + validatori)

4) Pubblicazione (Publish)
- Responsabilità: generare metadati (titolo, descrizione, cover), estrarre clip/short, pubblicare sui social e gestire code di pubblicazione.
- Componenti:
  - Servizio `services/publisher.py` con adapter per YouTube/Instagram/TikTok/Facebook/X
  - Coda `publish_queue` nel DB e worker `scripts/worker_publisher.py`

## Relazioni tra moduli
- Topic Management produce record in `areas`, `contents` (draft) e `schedule`.
- Generazione Video legge `schedule` per job in `pending`, scrive media su `storage/` e metadati in `media`, aggiorna `contents` (testo, durate, stato) e crea sottotitoli.
- Revisione consuma contenuti in stato `generating` o `reviewing`, aggiorna esito e note in `contents` e `media`.
- Pubblicazione prende elementi `ready` in `publish_queue`, interagisce con API dei social, e aggiorna stato pubblicazione su `publish_queue` e link nel record `contents`.

## Flusso dati
```
Utente/API → areas/topics/schedule → DB (areas, contents, schedule)
         → Scheduler → Job di generazione → LLM (testo) → DB (contents)
                                         → Image API → storage/img → DB (media)
                                         → TTS API → storage/audio → DB (media)
                                         → Assembler → storage/video + storage/subtitles → DB (media)
         → Review → DB (contents/media)
         → Publish → API Social → DB (publish_queue, contents)
```

## Schema DB (tabelle principali)

Di seguito le tabelle chiave con SQL di riferimento (PostgreSQL sintassi; in sviluppo si usa SQLite con adattamenti):

```sql
-- 1) Aree tematiche
CREATE TABLE areas (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  primary_social TEXT NOT NULL CHECK (primary_social IN ('youtube','instagram','tiktok','facebook','x')),
  logo_url TEXT,
  api_keys JSONB,            -- cifrare/gestire segreti in prod
  default_min_duration_min INT DEFAULT 5,
  default_max_duration_min INT DEFAULT 10,
  languages TEXT[] DEFAULT ARRAY['en','it','fr','de','es','hi','zh'],
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 2) Contenuti (un contenuto per argomento programmato)
CREATE TABLE contents (
  id SERIAL PRIMARY KEY,
  area_id INT NOT NULL REFERENCES areas(id) ON DELETE CASCADE,
  topic_title TEXT NOT NULL,
  micro_outline JSONB,       -- lista di sezioni (titolo, ordine)
  transcript JSONB,          -- testo per sezione + fonti
  duration_sec INT,
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','pending','generating','reviewing','ready','published','failed')),
  review_notes TEXT,
  publish_url TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 3) Schedule (pianificazione generazione/pubblicazione)
CREATE TABLE schedule (
  id SERIAL PRIMARY KEY,
  content_id INT NOT NULL REFERENCES contents(id) ON DELETE CASCADE,
  scheduled_at TIMESTAMP NOT NULL,
  action TEXT NOT NULL CHECK (action IN ('generate','publish')),
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','running','done','skipped','failed')),
  lock_token TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 4) Media (file generati: immagini, audio, video, sottotitoli)
CREATE TABLE media (
  id SERIAL PRIMARY KEY,
  content_id INT NOT NULL REFERENCES contents(id) ON DELETE CASCADE,
  type TEXT NOT NULL CHECK (type IN ('image','audio','video','subtitle','cover')),
  section_order INT,          -- per immagini/audio associati a sezione
  language TEXT,              -- per sottotitoli/audio
  path TEXT NOT NULL,         -- percorso su storage/
  metadata JSONB,             -- es. prompt, provider, durata, fps, dimensioni
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 5) Publish queue (coda di pubblicazione)
CREATE TABLE publish_queue (
  id SERIAL PRIMARY KEY,
  content_id INT NOT NULL REFERENCES contents(id) ON DELETE CASCADE,
  target_social TEXT NOT NULL CHECK (target_social IN ('youtube','instagram','tiktok','facebook','x')),
  title TEXT,
  description TEXT,
  tags TEXT[],
  cover_media_id INT REFERENCES media(id),
  clip_media_id INT REFERENCES media(id),
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','uploading','published','failed')),
  external_id TEXT,          -- id restituito dalla piattaforma
  error TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

Note:
- In SQLite sostituire `JSONB` con `TEXT` (JSON serializzato) e `ARRAY` con `TEXT` delimitato o tabelle di join.
- Migrazioni consigliate con Alembic.

## Interazione tra API e servizi
- Le API scrivono/leggono dal DB e mettono job nello `schedule`.
- I servizi batch (scheduler/worker) consumano dallo `schedule`, eseguono generazione/revisione/pubblicazione e aggiornano `contents`, `media`, `publish_queue`.
- I provider esterni (LLM/Immagini/TTS) sono incapsulati in adapter sostituibili via configurazione (`app.core.config.settings`).
# Workflow operativo

Questo documento descrive la pipeline end‑to‑end del sistema, con riferimenti ai moduli Python e alle configurazioni principali.

## 1) Topic Management

### 1.1 Generazione argomenti (idee non duplicate)
- Input: `area_id`, `count`
- Processo:
  - Recupera contesto dell'area (`areas.languages`, durata video di default)
  - LLM genera una lista di idee con punteggio di unicità
  - Deduplica contro `contents.topic_title`
  - Inserisce/aggiorna record in `contents` con stato `draft`
- Moduli Python:
  - `app.api.routes.topics`
  - `app.services.topic_generator` (LLM + dedup)
  - `app.db.session` / modelli ORM
- Configurazione:
  - `settings.llm_provider`, `settings.llm_api_key`
  - Limite default conteggio idee

### 1.2 Calendarizzazione dei contenuti
- Input: lista di `content_id` e `scheduled_at`
- Processo:
  - Crea job in tabella `schedule` con `action='generate'`, `status='pending'`
  - Impedisce modifiche se `scheduled_at` < now()
  - Uno scheduler periodico (APScheduler) attiva i job pianificati
- Moduli Python:
  - `app.api.routes.schedules`
  - `scripts/worker_scheduler.py`
- Configurazione:
  - `settings.scheduler_interval_minutes`

## 2) Generazione Video

### 2.1 Definizione micro-argomenti (outline)
- Input: `content_id`
- Processo: genera 4–8 sezioni (100–150 parole ciascuna) con titoli ordinati
- Output: `contents.micro_outline`
- Moduli:
  - `app.services.content_generator.generate_outline`

### 2.2 Generazione contenuto testuale con fonti
- Input: `content_id`, `micro_outline`, durata target
- Processo: LLM genera testi per sezione con 1–3 fonti URL
- Output: `contents.transcript` (per-sezione: testo + fonti)
- Moduli:
  - `app.services.content_generator.generate_sections`
- Config:
  - `areas.default_min_duration_min`, `areas.default_max_duration_min`

### 2.3 Generazione immagini per micro-argomento
- Input: outline, stile immagine, formato
- Processo: call provider immagini; salva file in `storage/img/*`
- Output: record `media` type=`image`
- Moduli:
  - `app.services.image_generator`
- Config:
  - `settings.image_provider`, `settings.image_api_key`
  - Stile immagini per area (preset/parametri)

### 2.4 Generazione audio TTS
- Input: `transcript`
- Processo: call provider TTS; salva wav/mp3 in `storage/audio/*`
- Output: record `media` type=`audio`, `language`
- Moduli:
  - `app.services.tts_generator`
- Config:
  - `settings.tts_provider`, `settings.tts_api_key`
  - Voce/lingua per area

### 2.5 Montaggio video + sottotitoli multilingua
- Input: audio, immagini, transcript
- Processo:
  - Assembla clip con immagine + testo sincronizzato alla lettura
  - Genera video finale e sottotitoli SRT/VTT per lingue: EN, IT, FR, DE, ES, HI, ZH
- Output: `media` type=`video` e `subtitle` multipli
- Moduli:
  - `app.services.video_assembler`
  - `app.services.subtitles_generator`
- Config:
  - Risoluzione, fps, font, layout; elenco lingue

## 3) Revisione
- Processo:
  - Verifica fonti (HTTP 200, contenuto coerente)
  - Fact-check con LLM (critique-pass)
  - Controllo plagio/parafrasi e sincronia audio/sottotitoli
  - Aggiorna `contents.status` e `review_notes`
- Moduli:
  - `app.services.review_pipeline`

## 4) Pubblicazione

### 4.1 Preparazione e pubblicazione per social
- Processo:
  - Genera cover (se mancante), titolo, descrizione, tag
  - Produce clip breve per short-form se richiesto
  - Enqueue in `publish_queue` e carica sui social
  - Aggiorna `publish_url` e stati
- Moduli:
  - `app.services.publisher`
  - `scripts/worker_publisher.py`
- Config:
  - Parametri specifici per piattaforma (limiti durata, aspect ratio, tag)

## Parametri e configurazione
- Durata video: per area (`areas.default_min_duration_min|max`), override a job
- Lingue sottotitoli: `settings.default_languages` o per area
- Stile immagini: preset per area (es. realistica, flat, anime), prompt di base
- Voce TTS: voce, velocità, lingua, prosodia
- Scheduler: intervallo, offset di tolleranza
- Storage: directory `settings.storage_dir`

## Error handling e retry
- Stati su `schedule` e `publish_queue` con `failed` e `error`
- Retry con backoff esponenziale per provider esterni
- Locking per job concorrenti via `schedule.lock_token`
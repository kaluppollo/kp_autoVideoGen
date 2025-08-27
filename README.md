# AutoVideo Studio

Piattaforma modulare per generare, revisionare e pubblicare video multi-social (YouTube, Instagram, TikTok, Facebook, X) a partire da aree tematiche e argomenti generati automaticamente. Include API, scheduler, servizi di generazione contenuti, immagini, TTS, montaggio video, sottotitoli e pubblicazione.

## Funzionalità principali
- Aree tematiche: creazione e gestione (nome, social principale, logo, chiavi API)
- Generazione argomenti: idee uniche e non duplicate per ciascuna area
- Calendarizzazione: pianificazione generazione/pubblicazione con rispetto dei vincoli temporali
- Generazione contenuti:
  - Micro-argomenti e sezioni
  - Testo con fonti (URL)
  - Immagini per sezione (provider configurabile)
  - Voce fuori campo TTS (provider configurabile)
  - Montaggio video automatico con sottotitoli multilingua (EN, IT, FR, DE, ES, HI, ZH)
- Revisione automatizzata: fact-check, verifica fonti, sincronie audio/sottotitoli
- Pubblicazione multi-social: titoli, cover, clip brevi, descrizioni e cross-link

## Requisiti di sistema
- Python 3.11+
- Pip + venv
- Facoltativo per sviluppo: Docker + Docker Compose
- Storage: spazio su disco per immagini, audio e video (cartella `storage/`)

## Installazione (sviluppo)
1. Clona il repository
2. Crea ed attiva un virtualenv
```bash
python -m venv .venv
source .venv/bin/activate
```
3. Installa dipendenze
```bash
pip install -r requirements.txt
```
4. Configura variabili ambiente
```bash
cp .env.example .env
# Modifica .env per provider LLM/Immagini/TTS se necessario
```
5. Avvia l'API
```bash
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```
6. Verifica healthcheck
```bash
curl http://localhost:8000/health/
```

### Avvio con Docker (opzionale)
```bash
docker compose up --build
```

## Esempio di utilizzo
- Crea area tematica (placeholder — persistenza DB sarà aggiunta):
```bash
curl -X POST http://localhost:8000/thematic-areas/ \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Filosofia",
    "primary_social": "youtube",
    "logo_url": null,
    "api_keys": {"openai": "sk-..."}
  }'
```
- Genera argomenti per area `id=1` (placeholder):
```bash
curl -X POST 'http://localhost:8000/topics/generate?area_id=1&count=10'
```

## Struttura del progetto
```
app/
  api/
    main.py                # FastAPI app e router
    routes/                # Endpoints REST (aree, topics, schedule)
  core/
    config.py              # Configurazione (pydantic-settings)
  db/
    session.py             # Engine e session factory
    models/                # Modelli ORM (da implementare)
  schemas/                 # Schemi Pydantic
  services/                # Servizi (content, image, tts, video, subtitles, review, publish)
  utils/                   # Utility condivise
scripts/                   # Scheduler/worker CLI
docs/                      # Documentazione (workflow)
db/                        # DB locale (sqlite dev)
storage/                   # Asset generati (img, audio, video)
```

## Roadmap
- v0.1 (MVP API + scheduler)
  - Modelli ORM e migrazioni
  - Persistenza aree, argomenti, schedule
  - Generatore argomenti (LLM) con dedup
  - Scheduler APScheduler + job di generazione
- v0.2 (Generazione contenuti)
  - Micro-argomenti e testo con fonti
  - Integrazione provider immagini (Stability/Midjourney) e TTS (Azure/ElevenLabs)
  - Montaggio video base + SRT multilingua
- v0.3 (Revisione e pubblicazione)
  - Revisore automatico (fact-check + critique-pass)
  - Pubblicazione multi-social (YouTube/Instagram/TikTok/Facebook/X)
  - Cover e clip per short-form
- v1.0
  - Dashboard web
  - Multi-tenant
  - Monitoraggio e metriche, code di lavorazione

## Licenza
MIT (da definire)
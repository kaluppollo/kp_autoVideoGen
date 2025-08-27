# Funzionalità 2.1: Definizione dei Micro-Argomenti

## Descrizione
La funzionalità 2.1 implementa la **definizione dei micro-argomenti**, ossia i titoli delle sezioni con cui è composto il video. Ogni sezione rappresenta un blocco di circa 100-150 parole e contribuisce alla struttura complessiva del video educativo.

## Implementazione

### Servizio principale: `MicroTopicsGenerator`
Localizzato in `app/services/content_generator.py`, il servizio fornisce:

- **Generazione intelligente**: Usa LLM (OpenAI GPT-4o-mini) per creare strutture specifiche per area tematica
- **Fallback robusto**: Sistema di fallback senza API per sviluppo e testing
- **Calcolo automatico**: Determina il numero ottimale di sezioni basato sulla durata target
- **Configurabilità**: Parametri configurabili per parole per sezione e durata

#### Caratteristiche tecniche:
- Supporto per prompt personalizzati per area tematica
- Validazione e sanificazione del JSON generato dall'LLM
- Gestione errori robusta con fallback
- Logging dettagliato per debugging

### Schemi Pydantic
Definiti in `app/schemas/content.py`:

- `MicroTopic`: Schema per singolo micro-argomento
- `MicroTopicsRequest`: Request per generazione
- `MicroTopicsResponse`: Response con statistiche

### API Endpoints

#### `POST /contents/generate-micro-topics`
Genera micro-argomenti senza salvare nel database.

**Request:**
```json
{
  "thematic_area": "filosofia",
  "specific_topic": "il mito della caverna di Platone",
  "target_duration_min": 7,
  "words_per_section": 125
}
```

**Response:**
```json
{
  "success": true,
  "micro_topics": [
    {
      "order": 1,
      "title": "Introduzione",
      "description": "Introduzione e panoramica di il mito della caverna di Platone",
      "estimated_words": 125,
      "key_points": ["Definizione iniziale", "Contesto generale", "Obiettivi della discussione"]
    }
  ],
  "total_sections": 7,
  "estimated_total_words": 875,
  "estimated_duration_min": 5.8
}
```

#### `POST /contents/{content_id}/apply-micro-topics`
Applica i micro-argomenti generati ad un contenuto esistente nel database.

### Configurazione

La funzionalità supporta diverse configurazioni tramite variabili d'ambiente:

```bash
# Provider LLM
LLM_PROVIDER="openai"
LLM_API_KEY="sk-your-openai-api-key-here"

# Defaults per la generazione video
DEFAULT_MIN_DURATION_MIN=5
DEFAULT_MAX_DURATION_MIN=10
```

## Logica di Funzionamento

### 1. Calcolo delle sezioni
```python
words_per_minute = 150  # Velocità di lettura standard
total_words = target_duration_min * words_per_minute
num_sections = max(3, min(8, int(total_words / words_per_section)))
```

### 2. Generazione con LLM
Il sistema invia un prompt strutturato all'LLM che include:
- Area tematica specifica
- Argomento del video
- Numero di sezioni calcolato
- Formato JSON richiesto

### 3. Fallback System
In caso di errore o mancanza di API key, il sistema usa template predefiniti:
- Introduzione
- Contesto storico
- Concetti fondamentali
- Analisi approfondita
- Dibattiti e critiche
- Rilevanza contemporanea
- Conclusioni

## Testing

### Test funzionali eseguiti:
✅ Generazione micro-argomenti per filosofia  
✅ Generazione micro-argomenti per psicologia  
✅ Applicazione al database  
✅ Validazione schemi Pydantic  
✅ Documentazione API automatica  

### Comandi di test:
```bash
# Test generazione standalone
curl -X POST "http://localhost:8000/contents/generate-micro-topics" \
  -H "Content-Type: application/json" \
  -d '{"thematic_area": "filosofia", "specific_topic": "il mito della caverna di Platone", "target_duration_min": 7, "words_per_section": 125}'

# Test applicazione a contenuto esistente
curl -X POST "http://localhost:8000/contents/1/apply-micro-topics" \
  -H "Content-Type: application/json" \
  -d '{"thematic_area": "filosofia", "specific_topic": "", "target_duration_min": 8, "words_per_section": 130}'
```

## Integrazione nel workflow

La funzionalità 2.1 si integra perfettamente nel flusso di generazione video:

1. **Input**: Area tematica + argomento specifico (dalla funzionalità 1.1)
2. **Elaborazione**: Generazione micro-argomenti strutturati
3. **Output**: Struttura dettagliata pronta per la funzionalità 2.2 (generazione contenuto)

### Stati del contenuto:
- `draft` → `pending` (dopo applicazione micro-argomenti)
- Pronto per il prossimo step: generazione del testo dettagliato

## Vantaggi dell'implementazione

- **Flessibilità**: Supporta diverse aree tematiche e stili
- **Scalabilità**: Facilmente estendibile per nuovi provider LLM
- **Robustezza**: Funziona anche senza API esterne
- **Precisione**: Calcoli automatici per durata e struttura
- **Tracciabilità**: Logging completo e gestione errori

## Prossimi passi

La funzionalità 2.1 pone le basi per:
- **Funzionalità 2.2**: Generazione contenuto testuale dettagliato
- **Funzionalità 2.3**: Generazione immagini per ogni micro-argomento
- **Funzionalità 2.4**: Generazione audio TTS
- **Funzionalità 2.5**: Montaggio video finale
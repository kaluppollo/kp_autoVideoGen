from typing import List, Dict, Optional
import httpx
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class MicroTopicsGenerator:
    """
    Servizio per la generazione di micro-argomenti (sezioni) per i video.
    
    Questa classe implementa la funzionalità 2.1: definizione dei micro argomenti,
    ossia i titoli delle sezioni con cui è composto il video (blocchi di circa 100-150 parole).
    """
    
    def __init__(self):
        self.llm_provider = settings.llm_provider
        self.api_key = settings.llm_api_key
        
    async def generate_micro_topics(
        self, 
        thematic_area: str, 
        specific_topic: str, 
        target_duration_min: int = 7,
        words_per_section: int = 125
    ) -> List[Dict]:
        """
        Genera micro-argomenti per un topic specifico di un'area tematica.
        
        Args:
            thematic_area: L'area tematica (es. "filosofia", "psicologia")
            specific_topic: L'argomento specifico (es. "il mito della caverna di Platone")
            target_duration_min: Durata target del video in minuti
            words_per_section: Numero di parole per sezione
            
        Returns:
            Lista di dizionari con i micro-argomenti:
            [
                {
                    "order": 1,
                    "title": "Introduzione al mito della caverna",
                    "description": "Breve descrizione del contenuto della sezione",
                    "estimated_words": 125,
                    "key_points": ["punto1", "punto2", "punto3"]
                },
                ...
            ]
        """
        
        # Calcola il numero approssimativo di sezioni basato sulla durata
        # Assumendo ~150 parole al minuto di lettura
        words_per_minute = 150
        total_words = target_duration_min * words_per_minute
        num_sections = max(3, min(8, int(total_words / words_per_section)))
        
        if self.llm_provider == "openai" and self.api_key:
            return await self._generate_with_openai(
                thematic_area, specific_topic, num_sections, words_per_section
            )
        else:
            # Fallback per sviluppo senza API key
            logger.warning("LLM API key non configurata, uso fallback statico")
            return self._generate_fallback(specific_topic, num_sections, words_per_section)
    
    async def _generate_with_openai(
        self, 
        thematic_area: str, 
        specific_topic: str, 
        num_sections: int,
        words_per_section: int
    ) -> List[Dict]:
        """Genera micro-argomenti usando OpenAI GPT."""
        
        prompt = f"""Sei un esperto di {thematic_area}. Devi creare una struttura dettagliata per un video educativo di circa {num_sections} sezioni sull'argomento "{specific_topic}".

Ogni sezione dovrebbe:
- Contenere circa {words_per_section} parole quando sviluppata
- Avere un titolo accattivante e descrittivo
- Includere 3-4 punti chiave da trattare
- Seguire un flusso logico e coinvolgente

Rispondi ESCLUSIVAMENTE con un JSON valido nel seguente formato:
[
  {{
    "order": 1,
    "title": "Titolo della sezione",
    "description": "Breve descrizione di cosa tratterà questa sezione",
    "estimated_words": {words_per_section},
    "key_points": ["punto1", "punto2", "punto3", "punto4"]
  }}
]

Area tematica: {thematic_area}
Argomento specifico: {specific_topic}
Numero di sezioni: {num_sections}"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "Sei un esperto di contenuti educativi. Rispondi sempre con JSON valido."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2000
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"].strip()
                    
                    # Parsing del JSON dal contenuto
                    try:
                        # Rimuovi eventuali backticks markdown
                        if content.startswith("```json"):
                            content = content[7:-3]
                        elif content.startswith("```"):
                            content = content[3:-3]
                        
                        micro_topics = json.loads(content)
                        
                        # Validazione della struttura
                        if isinstance(micro_topics, list) and len(micro_topics) > 0:
                            for i, topic in enumerate(micro_topics):
                                # Assicura che ci siano tutti i campi necessari
                                topic.setdefault("order", i + 1)
                                topic.setdefault("estimated_words", words_per_section)
                                if "key_points" not in topic:
                                    topic["key_points"] = []
                            
                            logger.info(f"Generati {len(micro_topics)} micro-argomenti per '{specific_topic}'")
                            return micro_topics
                        else:
                            logger.error("Formato JSON non valido dalla risposta OpenAI")
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"Errore parsing JSON da OpenAI: {e}")
                        logger.debug(f"Contenuto ricevuto: {content}")
                        
                else:
                    logger.error(f"Errore API OpenAI: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Errore chiamata OpenAI API: {e}")
        
        # Fallback in caso di errore
        return self._generate_fallback(specific_topic, num_sections, words_per_section)
    
    def _generate_fallback(
        self, 
        specific_topic: str, 
        num_sections: int, 
        words_per_section: int
    ) -> List[Dict]:
        """Generazione fallback senza LLM per sviluppo."""
        
        # Template base che si adatta al topic
        base_sections = [
            ("Introduzione", f"Introduzione e panoramica di {specific_topic}", 
             ["Definizione iniziale", "Contesto generale", "Obiettivi della discussione"]),
            ("Contesto storico", f"Background storico e origini di {specific_topic}", 
             ["Periodo storico", "Autori/figure chiave", "Influenze culturali"]),
            ("Concetti fondamentali", f"I principi e concetti chiave di {specific_topic}", 
             ["Definizioni principali", "Teoria di base", "Elementi distintivi"]),
            ("Analisi approfondita", f"Esame dettagliato degli aspetti di {specific_topic}", 
             ["Implicazioni teoriche", "Esempi pratici", "Interpretazioni moderne"]),
            ("Dibattiti e critiche", f"Controversie e diverse interpretazioni di {specific_topic}", 
             ["Critiche principali", "Dibattiti accademici", "Posizioni alternative"]),
            ("Rilevanza contemporanea", f"L'importanza di {specific_topic} oggi", 
             ["Applicazioni moderne", "Influenza attuale", "Sviluppi recenti"]),
            ("Conclusioni", f"Riflessioni finali su {specific_topic}", 
             ["Sintesi dei punti chiave", "Considerazioni finali", "Spunti per approfondimenti"])
        ]
        
        # Seleziona le sezioni più appropriate
        selected_sections = base_sections[:num_sections]
        
        micro_topics = []
        for i, (title, description, key_points) in enumerate(selected_sections):
            micro_topics.append({
                "order": i + 1,
                "title": title,
                "description": description,
                "estimated_words": words_per_section,
                "key_points": key_points
            })
        
        logger.info(f"Generato fallback con {len(micro_topics)} micro-argomenti per '{specific_topic}'")
        return micro_topics


# Funzioni di compatibilità con l'API esistente
def generate_outline(topic_title: str) -> List[Dict]:
    """Funzione di compatibilità - deprecata, usa MicroTopicsGenerator."""
    return [
        {"order": 1, "title": f"Introduzione a {topic_title}"},
        {"order": 2, "title": "Contesto storico"},
        {"order": 3, "title": "Concetti chiave"},
        {"order": 4, "title": "Impatto e conclusioni"},
    ]


def generate_sections(outline: List[Dict], words_per_section: int = 120) -> List[Dict]:
    """Funzione di compatibilità - deprecata, usa MicroTopicsGenerator."""
    sections = []
    for item in outline:
        sections.append({
            "order": item["order"],
            "text": f"Testo generato per la sezione '{item['title']}' (circa {words_per_section} parole)...",
            "sources": ["https://example.com/source1", "https://example.com/source2"],
        })
    return sections
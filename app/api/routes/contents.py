from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.contents_service import get_content, update_content
from app.services.content_generator import MicroTopicsGenerator
from app.services.areas_service import get_area
from app.schemas.content import (
    MicroTopicsRequest, 
    MicroTopicsResponse, 
    MicroTopic,
    ContentItem
)

router = APIRouter()


@router.post("/generate-micro-topics", response_model=MicroTopicsResponse)
async def generate_micro_topics(request: MicroTopicsRequest):
    """
    Funzionalità 2.1: Genera micro-argomenti per un video.
    
    Genera i titoli delle sezioni (micro-argomenti) con cui è composto il video,
    dove ogni sezione rappresenta un blocco di circa 100-150 parole.
    """
    try:
        generator = MicroTopicsGenerator()
        micro_topics_data = await generator.generate_micro_topics(
            thematic_area=request.thematic_area,
            specific_topic=request.specific_topic,
            target_duration_min=request.target_duration_min,
            words_per_section=request.words_per_section
        )
        
        # Converti i dati in schema Pydantic
        micro_topics = [MicroTopic(**topic) for topic in micro_topics_data]
        
        # Calcola statistiche
        total_sections = len(micro_topics)
        estimated_total_words = sum(topic.estimated_words for topic in micro_topics)
        estimated_duration_min = estimated_total_words / 150  # ~150 parole al minuto
        
        return MicroTopicsResponse(
            success=True,
            micro_topics=micro_topics,
            total_sections=total_sections,
            estimated_total_words=estimated_total_words,
            estimated_duration_min=round(estimated_duration_min, 1)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Errore nella generazione dei micro-argomenti: {str(e)}"
        )


@router.post("/{content_id}/apply-micro-topics", response_model=ContentItem)
async def apply_micro_topics_to_content(
    content_id: int = Path(..., description="ID del contenuto"),
    request: MicroTopicsRequest = ...,
    db: Session = Depends(get_db)
):
    """
    Applica i micro-argomenti generati ad un contenuto esistente nel database.
    
    Questo endpoint:
    1. Genera i micro-argomenti per il contenuto specificato
    2. Aggiorna il campo micro_outline del contenuto nel database
    3. Calcola la durata stimata del video
    """
    # Verifica che il contenuto esista
    content = get_content(db, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Contenuto non trovato")
    
    # Verifica che l'area tematica esista
    area = get_area(db, content.area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area tematica non trovata")
    
    try:
        # Genera i micro-argomenti
        generator = MicroTopicsGenerator()
        
        # Se non specificato, usa il nome dell'area e il titolo del topic dal database
        thematic_area = request.thematic_area or area.name
        specific_topic = request.specific_topic or content.topic_title
        
        micro_topics_data = await generator.generate_micro_topics(
            thematic_area=thematic_area,
            specific_topic=specific_topic,
            target_duration_min=request.target_duration_min,
            words_per_section=request.words_per_section
        )
        
        # Calcola la durata stimata in secondi
        estimated_total_words = sum(topic.get("estimated_words", 125) for topic in micro_topics_data)
        estimated_duration_sec = int((estimated_total_words / 150) * 60)  # ~150 parole al minuto
        
        # Aggiorna il contenuto nel database
        update_data = {
            "micro_outline": micro_topics_data,
            "duration_sec": estimated_duration_sec,
            "status": "pending"  # Pronto per il prossimo step (generazione testo)
        }
        
        updated_content = update_content(db, content, update_data)
        
        return ContentItem.model_validate(updated_content)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Errore nell'applicazione dei micro-argomenti: {str(e)}"
        )


@router.get("/{content_id}", response_model=ContentItem)
def get_content_details(content_id: int = Path(...), db: Session = Depends(get_db)):
    """Ottieni i dettagli di un contenuto specifico."""
    content = get_content(db, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Contenuto non trovato")
    
    return ContentItem.model_validate(content)
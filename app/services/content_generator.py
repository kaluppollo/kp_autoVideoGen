from typing import List, Dict


def generate_outline(topic_title: str) -> List[Dict]:
    return [
        {"order": 1, "title": f"Introduzione a {topic_title}"},
        {"order": 2, "title": "Contesto storico"},
        {"order": 3, "title": "Concetti chiave"},
        {"order": 4, "title": "Impatto e conclusioni"},
    ]


def generate_sections(outline: List[Dict], words_per_section: int = 120) -> List[Dict]:
    sections = []
    for item in outline:
        sections.append({
            "order": item["order"],
            "text": f"Testo generato per la sezione '{item['title']}' (circa {words_per_section} parole)...",
            "sources": ["https://example.com/source1", "https://example.com/source2"],
        })
    return sections
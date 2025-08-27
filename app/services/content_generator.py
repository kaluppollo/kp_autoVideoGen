from typing import List, Dict


def generate_outline(
    topic_title: str,
    min_sections: int = 4,
    max_sections: int = 8,
) -> List[Dict]:
    """Generate a deterministic outline with 4–8 ordered section titles.

    This is a placeholder implementation that does not call an LLM yet.
    It provides stable output across runs for the same topic and keeps
    the number of sections within the requested range.
    """
    if min_sections < 1:
        min_sections = 1
    if max_sections < min_sections:
        max_sections = min_sections

    # Deterministic count in [min_sections, max_sections]
    span = (max_sections - min_sections + 1)
    num_sections = min_sections if span <= 1 else (min_sections + (abs(hash(topic_title)) % span))

    candidates = [
        f"Introduzione a {topic_title}",
        "Origini e contesto",
        "Concetti fondamentali",
        "Esempi e casi studio",
        "Critiche e dibattiti",
        "Applicazioni pratiche",
        "Impatto culturale e attuale",
        "Sintesi e conclusioni",
    ]
    titles = candidates[: max(1, min(num_sections, len(candidates)))]

    outline: List[Dict] = []
    for index, title in enumerate(titles, start=1):
        outline.append({"order": index, "title": title})
    return outline


def generate_sections(outline: List[Dict], words_per_section: int = 120) -> List[Dict]:
    sections = []
    for item in outline:
        sections.append({
            "order": item["order"],
            "text": f"Testo generato per la sezione '{item['title']}' (circa {words_per_section} parole)...",
            "sources": ["https://example.com/source1", "https://example.com/source2"],
        })
    return sections
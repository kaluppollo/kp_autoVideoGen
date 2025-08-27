from typing import List
from app.schemas.topic import TopicIdea


def generate_topic_ideas(area_name: str, count: int = 10) -> List[TopicIdea]:
    # Placeholder: restituisce idee fittizie. Integrare con LLM in seguito.
    ideas = []
    for i in range(count):
        title = f"Idea {i+1} per {area_name}"
        ideas.append(TopicIdea(title=title, uniqueness_score=0.9))
    return ideas
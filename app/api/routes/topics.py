from typing import List
from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/")
def list_topics(area_id: int | None = Query(default=None)):
    # TODO: implement DB-backed listing
    return []


@router.post("/generate")
def generate_topics(area_id: int, count: int = 10):
    # TODO: call services.topic_generator.generate_topic_ideas
    return {"area_id": area_id, "generated": count, "items": []}
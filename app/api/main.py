from fastapi import FastAPI

from app.core.config import settings
from app.api.routes.health import router as health_router
from app.api.routes.thematic_areas import router as thematic_router
from app.api.routes.topics import router as topics_router
from app.api.routes.schedules import router as schedules_router
from app.api.routes.contents import router as contents_router


app = FastAPI(title=settings.app_name)

# Routers
app.include_router(health_router, prefix="/health", tags=["health"]) 
app.include_router(thematic_router, prefix="/thematic-areas", tags=["thematic-areas"]) 
app.include_router(topics_router, prefix="/topics", tags=["topics"]) 
app.include_router(schedules_router, prefix="/schedules", tags=["schedules"]) 
app.include_router(contents_router, prefix="/contents", tags=["contents"]) 


@app.get("/")
async def root():
    return {"app": settings.app_name, "env": settings.environment}
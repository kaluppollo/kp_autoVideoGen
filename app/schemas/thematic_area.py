from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict


class ThematicAreaBase(BaseModel):
    name: str = Field(description="Nome dell'area tematica, es. Filosofia")
    primary_social: str = Field(description="Social principale: youtube | instagram | tiktok | facebook | x")
    logo_url: Optional[HttpUrl] = Field(default=None, description="URL del logo")
    api_keys: Optional[Dict[str, str]] = Field(default=None, description="Mappa provider->api_key, cifrata in produzione")


class ThematicAreaCreate(ThematicAreaBase):
    pass


class ThematicArea(ThematicAreaBase):
    id: int

    class Config:
        from_attributes = True
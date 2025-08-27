from sqlalchemy import Column, Integer, String, Text, DateTime, func, JSON
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SAEnum
import enum

from app.db.models.base import Base


class SocialPlatform(str, enum.Enum):
    youtube = "youtube"
    instagram = "instagram"
    tiktok = "tiktok"
    facebook = "facebook"
    x = "x"


class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    primary_social = Column(SAEnum(SocialPlatform, name="social_platform", native_enum=False), nullable=False)
    logo_url = Column(Text, nullable=True)
    api_keys = Column(JSON, nullable=True)
    default_min_duration_min = Column(Integer, nullable=False, server_default="5")
    default_max_duration_min = Column(Integer, nullable=False, server_default="10")
    languages = Column(JSON, nullable=False, server_default='["en","it","fr","de","es","hi","zh"]')

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
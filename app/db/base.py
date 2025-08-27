from app.db.models.base import Base

# Import models here so Alembic can discover them via Base.metadata
from app.db.models.area import Area  # noqa: F401
from app.db.models.content import Content  # noqa: F401
from app.db.models.schedule import Schedule  # noqa: F401
from app.db.models.media import Media  # noqa: F401
from app.db.models.publish_queue import PublishQueue  # noqa: F401
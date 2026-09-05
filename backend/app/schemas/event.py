from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Event(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    event_id: int | None = None
    event_type: str
    track_id: int
    camera_id: str
    timestamp: datetime
    severity: str
    message: str
    metadata: dict
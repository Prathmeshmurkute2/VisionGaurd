from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ZonePoint(BaseModel):
    """A single polygon vertex, normalized to 0.0-1.0 (fraction of
    frame width/height), so the zone is resolution-independent."""

    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)


class ZoneCreate(BaseModel):

    camera_id: str
    name: str = "Restricted Zone"
    zone_type: str = "intrusion"
    points: list[ZonePoint]

    @field_validator("points")
    @classmethod
    def at_least_three_points(cls, points):

        if len(points) < 3:
            raise ValueError(
                "A zone polygon needs at least 3 points."
            )

        return points


class ZoneUpdate(BaseModel):

    name: str | None = None
    points: list[ZonePoint] | None = None
    is_active: bool | None = None


class ZoneResponse(BaseModel):

    id: int
    camera_id: str
    name: str
    zone_type: str
    points: list[ZonePoint]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

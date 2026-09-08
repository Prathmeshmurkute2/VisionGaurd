from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime
from datetime import datetime

from app.database.base import Base


class ZoneModel(Base):

    __tablename__ = "zones"

    id = Column(Integer, primary_key=True)

    camera_id = Column(String, nullable=False, index=True)

    name = Column(String, nullable=False, default="Restricted Zone")

    zone_type = Column(String, nullable=False, default="intrusion")

    # List of {"x": float, "y": float} points, normalized to the
    # 0.0-1.0 range (fraction of frame width/height) so the zone
    # stays correct regardless of the actual video resolution.
    points = Column(JSON, nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

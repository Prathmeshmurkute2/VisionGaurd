from sqlalchemy.orm import Session

from app.database.models import ZoneModel


class ZoneRepository:

    def create(self, db: Session, camera_id, name, zone_type, points):

        db_zone = ZoneModel(
            camera_id=camera_id,
            name=name,
            zone_type=zone_type,
            points=[p.model_dump() for p in points],
            is_active=True,
        )

        db.add(db_zone)
        db.commit()
        db.refresh(db_zone)

        return db_zone

    def get_by_id(self, db: Session, zone_id: int):

        return (
            db.query(ZoneModel)
            .filter(ZoneModel.id == zone_id)
            .first()
        )

    def list_by_camera(self, db: Session, camera_id: str):

        return (
            db.query(ZoneModel)
            .filter(ZoneModel.camera_id == camera_id)
            .order_by(ZoneModel.created_at.desc())
            .all()
        )

    def get_active_by_camera(self, db: Session, camera_id: str, zone_type="intrusion"):

        return (
            db.query(ZoneModel)
            .filter(
                ZoneModel.camera_id == camera_id,
                ZoneModel.zone_type == zone_type,
                ZoneModel.is_active.is_(True),
            )
            .order_by(ZoneModel.created_at.desc())
            .first()
        )

    def update(self, db: Session, db_zone: ZoneModel, updates: dict):

        for key, value in updates.items():
            setattr(db_zone, key, value)

        db.commit()
        db.refresh(db_zone)

        return db_zone

    def delete(self, db: Session, db_zone: ZoneModel):

        db.delete(db_zone)
        db.commit()


zone_repository = ZoneRepository()

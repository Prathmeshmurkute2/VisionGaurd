from sqlalchemy.orm import Session

from app.repositories.zone_repository import zone_repository
from app.schemas.zone import ZoneCreate, ZoneUpdate, ZoneResponse
from app.exceptions.zone import ZoneNotFoundException


class ZoneService:

    def create_zone(self, db: Session, request: ZoneCreate):

        # Only one active intrusion zone per camera for now (keeps
        # the detector/UI simple) - deactivate any existing one.
        existing = zone_repository.get_active_by_camera(
            db, request.camera_id, request.zone_type
        )

        if existing is not None:
            zone_repository.update(db, existing, {"is_active": False})

        db_zone = zone_repository.create(
            db=db,
            camera_id=request.camera_id,
            name=request.name,
            zone_type=request.zone_type,
            points=request.points,
        )

        self._apply_to_live_camera(request.camera_id, db_zone)

        return ZoneResponse.model_validate(db_zone)

    def update_zone(self, db: Session, zone_id: int, request: ZoneUpdate):

        db_zone = zone_repository.get_by_id(db, zone_id)

        if db_zone is None:
            raise ZoneNotFoundException()

        updates = {}

        if request.name is not None:
            updates["name"] = request.name

        if request.points is not None:
            updates["points"] = [p.model_dump() for p in request.points]

        if request.is_active is not None:
            updates["is_active"] = request.is_active

        db_zone = zone_repository.update(db, db_zone, updates)

        self._apply_to_live_camera(db_zone.camera_id, db_zone)

        return ZoneResponse.model_validate(db_zone)

    def delete_zone(self, db: Session, zone_id: int):

        db_zone = zone_repository.get_by_id(db, zone_id)

        if db_zone is None:
            raise ZoneNotFoundException()

        camera_id = db_zone.camera_id

        zone_repository.delete(db, db_zone)

        self._apply_to_live_camera(camera_id, None)

    def list_zones(self, db: Session, camera_id: str):

        db_zones = zone_repository.list_by_camera(db, camera_id)

        return [ZoneResponse.model_validate(z) for z in db_zones]

    def _apply_to_live_camera(self, camera_id: str, db_zone):
        """
        If the edited zone belongs to the camera that's currently
        running, push the change into the live detector immediately
        rather than requiring a restart.
        """

        from app.core.constants import DEFAULT_CAMERA_ID

        if camera_id != DEFAULT_CAMERA_ID:
            return

        # Imported here (not at module load, and only once we know
        # it's actually needed) to avoid forcing the heavy video
        # pipeline (YOLO/pose models) to load just for an unrelated
        # camera's zone edit.
        from app.services.video_service import video_service

        if db_zone is None or not db_zone.is_active:
            video_service.update_intrusion_zone(None)
        else:
            video_service.update_intrusion_zone(db_zone.points)


zone_service = ZoneService()

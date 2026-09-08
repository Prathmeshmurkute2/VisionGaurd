from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.dependencies import get_db
from app.database.models import UserModel
from app.schemas.api_response import ApiResponse
from app.schemas.zone import ZoneCreate, ZoneUpdate
from app.services.zone_service import zone_service

router = APIRouter(
    prefix="/zones",
    tags=["Zones"],
)


@router.get("")
def list_zones(
    camera_id: str,
    db: Annotated[Session, Depends(get_db)],
):

    zones = zone_service.list_zones(db=db, camera_id=camera_id)

    return ApiResponse(
        message="Zones retrieved successfully.",
        data=zones,
    )


@router.post("")
def create_zone(
    request: ZoneCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
):

    zone = zone_service.create_zone(db=db, request=request)

    return ApiResponse(
        message="Zone created successfully.",
        data=zone,
    )


@router.put("/{zone_id}")
def update_zone(
    zone_id: int,
    request: ZoneUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
):

    zone = zone_service.update_zone(db=db, zone_id=zone_id, request=request)

    return ApiResponse(
        message="Zone updated successfully.",
        data=zone,
    )


@router.delete("/{zone_id}")
def delete_zone(
    zone_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
):

    zone_service.delete_zone(db=db, zone_id=zone_id)

    return ApiResponse(
        message="Zone deleted successfully.",
        data=None,
    )

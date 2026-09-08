from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.auth.dependencies import get_current_user
from app.database.models import UserModel
from app.services.video_service import video_service

router = APIRouter(
    prefix="/camera",
    tags=["Camera"],
)


@router.post("/start")
def start_camera(
    current_user: Annotated[UserModel, Depends(get_current_user)],
):

    video_service.start_camera()

    return {
        "success": True,
        "message": "Camera started successfully.",
    }


@router.post("/stop")
def stop_camera(
    current_user: Annotated[UserModel, Depends(get_current_user)],
):

    video_service.stop_camera()

    return {
        "success": True,
        "message": "Camera stopped successfully.",
    }


@router.get("/stream")
def stream_camera():

    return StreamingResponse(
        video_service.generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@router.get("/status")
def camera_status():

    return {
        "success": True,
        "running": video_service.is_running,
    }
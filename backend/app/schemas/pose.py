from pydantic import BaseModel

from app.schemas.bounding_box import BoundingBox


class Keypoint(BaseModel):
    x: float
    y: float
    confidence: float


class PosePerson(BaseModel):
    """
    A single tracked person plus their estimated skeleton keypoints,
    in COCO's 17-keypoint order:

        0 nose, 1 left_eye, 2 right_eye, 3 left_ear, 4 right_ear,
        5 left_shoulder, 6 right_shoulder, 7 left_elbow, 8 right_elbow,
        9 left_wrist, 10 right_wrist, 11 left_hip, 12 right_hip,
        13 left_knee, 14 right_knee, 15 left_ankle, 16 right_ankle
    """

    track_id: int
    bbox: BoundingBox
    keypoints: list[Keypoint]

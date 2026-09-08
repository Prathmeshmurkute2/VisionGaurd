from app.detection.pose import pose_detector
from app.schemas.pose import Keypoint, PosePerson
from app.schemas.bounding_box import BoundingBox


class PoseTracker:
    """
    Runs the pose model with ByteTrack so keypoints stay attached to
    a consistent track_id across frames (needed to tell "just sat
    down" apart from "has been sitting for an hour").
    """

    def __init__(self):
        self.model = pose_detector.get_model()

    def track(self, frame) -> list[PosePerson]:

        results = self.model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False,
        )

        pose_people = []

        for result in results:

            if result.boxes.id is None or result.keypoints is None:
                continue

            boxes = result.boxes
            keypoints_data = result.keypoints.data  # (N, 17, 3) tensor

            for i in range(len(boxes)):

                track_id = int(boxes.id[i].item())

                x1, y1, x2, y2 = boxes.xyxy[i].tolist()

                bbox = BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)

                raw_keypoints = keypoints_data[i].tolist()

                keypoints = [
                    Keypoint(x=kp[0], y=kp[1], confidence=kp[2])
                    for kp in raw_keypoints
                ]

                pose_people.append(
                    PosePerson(
                        track_id=track_id,
                        bbox=bbox,
                        keypoints=keypoints,
                    )
                )

        return pose_people


pose_tracker = PoseTracker()

from app.detection.yolo import detector
from app.schemas.detection import Detection
from app.schemas.tracked_object import TrackedObject
from app.schemas.bounding_box import BoundingBox
from app.core.constants import THREAT_OBJECT_CLASSES


class Tracker:
    """
    Handles multi-object tracking using ByteTrack.

    Tracks persons (for movement/zone/crowd analytics) plus any
    threat-object classes the loaded model knows about (see
    THREAT_OBJECT_CLASSES) - which requires a model fine-tuned for
    weapon detection, since the default COCO weights don't include them.
    """

    TRACKED_CLASSES = {"person"} | THREAT_OBJECT_CLASSES

    def __init__(self):
        self.model = detector.get_model()

    def track(self, frame):

        results = self.model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False,
        )

        tracked_objects = []

        for result in results:

            if result.boxes.id is None:
                continue

            for box in result.boxes:

                class_id = int(box.cls.item())
                class_name = result.names[class_id]

                # -----------------------------------------
                # Track only persons and threat objects
                # -----------------------------------------
                if class_name not in self.TRACKED_CLASSES:
                    continue

                coordinates = box.xyxy[0].tolist()

                bbox = BoundingBox(
                    x1=coordinates[0],
                    y1=coordinates[1],
                    x2=coordinates[2],
                    y2=coordinates[3],
                )

                detection = Detection(
                    class_id=class_id,
                    class_name=class_name,
                    confidence=float(box.conf.item()),
                    bbox=bbox,
                )

                tracked_object = TrackedObject(
                    track_id=int(box.id.item()),
                    detection=detection,
                )

                tracked_objects.append(tracked_object)

        return tracked_objects


tracker = Tracker()
from app.core.constants import SEVERITY_CRITICAL, THREAT_OBJECT_CLASSES


class ThreatObjectDetector:
    """
    Flags detections of dangerous objects (guns, knives, etc).

    IMPORTANT: the default YOLO/COCO weights (yolo11n.pt) cannot
    detect weapons - COCO's 80 classes don't include them. This
    detector only produces alerts once YOLO_MODEL is pointed at a
    model fine-tuned on a weapon-detection dataset whose class
    names match THREAT_OBJECT_CLASSES (app/core/constants.py).
    Until then this module is a no-op by design, not a bug.
    """

    def __init__(self, cooldown_seconds=10):

        self.cooldown_seconds = cooldown_seconds
        self.last_alert_time = {}

    def check(self, tracked_objects):

        import time

        events = []
        now = time.time()

        for tracked_object in tracked_objects:

            class_name = tracked_object.detection.class_name

            if class_name not in THREAT_OBJECT_CLASSES:
                continue

            track_id = tracked_object.track_id
            last_alert = self.last_alert_time.get(track_id, 0)

            if now - last_alert < self.cooldown_seconds:
                continue

            self.last_alert_time[track_id] = now

            events.append({
                "track_id": track_id,
                "event_type": "threat_object",
                "severity": SEVERITY_CRITICAL,
                "message": f"Detected dangerous object: {class_name}",
                "object_class": class_name,
                "confidence": tracked_object.detection.confidence,
            })

        return events

    def reset(self):

        self.last_alert_time.clear()

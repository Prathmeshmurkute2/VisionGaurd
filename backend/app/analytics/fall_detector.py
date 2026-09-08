import time

from app.core.constants import SEVERITY_WARNING


class FallDetector:
    """
    Heuristic fall detector: a standing person's bounding box is
    tall and narrow (height > width). If it flips to wide and short
    within a short time window, that's consistent with someone
    going from standing to lying down quickly - a fall, being
    knocked down, or collapsing.

    Like the other heuristics here, this is a proxy signal, not a
    trained pose/action model. It will false-positive on someone
    bending down quickly, sitting on the floor, or a bad detection
    box, and it can miss slow falls. Best treated as "worth a human
    glance".
    """

    STANDING_RATIO = 1.2   # height / width - "tall and narrow"
    FALLEN_RATIO = 0.8     # height / width - "short and wide"

    def __init__(self, window_seconds=1.5, cooldown_seconds=10):

        self.window_seconds = window_seconds
        self.cooldown_seconds = cooldown_seconds

        # track_id -> (timestamp, ratio) of the most recent
        # "standing" observation
        self.last_standing = {}

        self.last_alert_time = {}

    def check(self, tracked_objects):

        events = []
        now = time.time()

        for tracked_object in tracked_objects:

            if tracked_object.detection.class_name != "person":
                continue

            track_id = tracked_object.track_id
            bbox = tracked_object.detection.bbox

            width = max(bbox.x2 - bbox.x1, 1)
            height = max(bbox.y2 - bbox.y1, 1)
            ratio = height / width

            if ratio >= self.STANDING_RATIO:
                self.last_standing[track_id] = now
                continue

            if ratio > self.FALLEN_RATIO:
                # Ambiguous middle ground - not clearly fallen
                continue

            standing_time = self.last_standing.get(track_id)

            if standing_time is None:
                continue

            elapsed = now - standing_time

            if elapsed > self.window_seconds:
                continue

            last_alert = self.last_alert_time.get(track_id, 0)

            if now - last_alert < self.cooldown_seconds:
                continue

            self.last_alert_time[track_id] = now

            events.append({
                "track_id": track_id,
                "event_type": "possible_fall",
                "severity": SEVERITY_WARNING,
                "message": (
                    "Person went from standing to lying down "
                    "quickly - possible fall, review footage"
                ),
                "seconds_since_standing": round(elapsed, 2),
            })

        return events

    def reset(self):

        self.last_standing.clear()
        self.last_alert_time.clear()

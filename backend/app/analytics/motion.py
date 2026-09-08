import time

from app.core.constants import SEVERITY_WARNING


class RunningDetector:
    """
    Flags sudden fast movement (e.g. running, or a struggle) by
    measuring how fast each person's bounding-box centroid moves,
    in pixels/second, between consecutive processed frames.

    Note: since frames are throttled to PROCESSING_FPS, the
    speed_threshold is naturally in "pixels per second of real
    time", not per-frame - it doesn't need retuning if the FPS
    setting changes.
    """

    def __init__(self, speed_threshold, cooldown_seconds=5):

        self.speed_threshold = speed_threshold
        self.cooldown_seconds = cooldown_seconds

        # track_id -> (x, y, timestamp) of last position
        self.last_position = {}

        # track_id -> timestamp of last alert (debounce)
        self.last_alert_time = {}

    def check(self, tracked_objects):

        events = []
        now = time.time()

        for tracked_object in tracked_objects:

            if tracked_object.detection.class_name != "person":
                continue

            track_id = tracked_object.track_id
            x, y = tracked_object.detection.bbox.center

            previous = self.last_position.get(track_id)
            self.last_position[track_id] = (x, y, now)

            if previous is None:
                continue

            prev_x, prev_y, prev_time = previous
            dt = now - prev_time

            if dt <= 0:
                continue

            distance = ((x - prev_x) ** 2 + (y - prev_y) ** 2) ** 0.5
            speed = distance / dt

            if speed < self.speed_threshold:
                continue

            last_alert = self.last_alert_time.get(track_id, 0)

            if now - last_alert < self.cooldown_seconds:
                continue

            self.last_alert_time[track_id] = now

            events.append({
                "track_id": track_id,
                "event_type": "fast_movement",
                "severity": SEVERITY_WARNING,
                "message": "Person moving unusually fast (possible running)",
                "speed_px_per_sec": round(speed, 1),
            })

        return events

    def reset(self):

        self.last_position.clear()
        self.last_alert_time.clear()

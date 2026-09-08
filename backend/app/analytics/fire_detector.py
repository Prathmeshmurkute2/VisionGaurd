import time

import cv2
import numpy as np

from app.core.constants import SEVERITY_CRITICAL


class FireDetector:
    """
    Heuristic fire/flame detection based on color.

    This is NOT a trained model - it thresholds the frame in HSV
    space for flame-like orange/red/yellow tones and checks how
    much of the frame is covered. It's a reasonable first line of
    defense for something like a petrol station (bright orange
    flame against a much less saturated background) but it WILL
    false-positive on things like orange safety vests, sunsets in
    frame, or warm lighting. For production use, replace this with
    a proper fire/smoke detection model (e.g. a YOLO model
    fine-tuned on a fire dataset) - the check() interface
    (frame in, events out) stays the same either way.
    """

    # Two HSV ranges to catch both reddish and yellowish flame tones
    LOWER_FIRE_1 = np.array([0, 120, 150])
    UPPER_FIRE_1 = np.array([25, 255, 255])

    LOWER_FIRE_2 = np.array([160, 120, 150])
    UPPER_FIRE_2 = np.array([180, 255, 255])

    def __init__(self, min_area_ratio=0.02, cooldown_seconds=15):

        self.min_area_ratio = min_area_ratio
        self.cooldown_seconds = cooldown_seconds
        self.last_alert_time = 0.0

    def check(self, frame):

        events = []
        now = time.time()

        if now - self.last_alert_time < self.cooldown_seconds:
            return events

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, self.LOWER_FIRE_1, self.UPPER_FIRE_1)
        mask |= cv2.inRange(hsv, self.LOWER_FIRE_2, self.UPPER_FIRE_2)

        fire_pixels = int(cv2.countNonZero(mask))
        total_pixels = frame.shape[0] * frame.shape[1]

        ratio = fire_pixels / total_pixels

        if ratio < self.min_area_ratio:
            return events

        self.last_alert_time = now

        events.append({
            "track_id": 0,
            "event_type": "fire_detected",
            "severity": SEVERITY_CRITICAL,
            "message": f"Possible fire/flame detected ({ratio:.1%} of frame)",
            "frame_coverage": round(ratio, 4),
        })

        return events

    def reset(self):

        self.last_alert_time = 0.0

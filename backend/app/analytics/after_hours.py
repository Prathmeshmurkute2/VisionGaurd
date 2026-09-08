from datetime import datetime

from app.core.constants import SEVERITY_CRITICAL


class AfterHoursDetector:
    """
    Flags any person present outside the configured business hours,
    e.g. between 22:00 and 06:00. Handles the overnight wraparound
    (start_hour > end_hour) correctly.

    Fires once per continuous presence per track, to avoid spamming
    an alert every frame while the person remains on camera.
    """

    def __init__(self, start_hour, end_hour):

        self.start_hour = start_hour
        self.end_hour = end_hour

        self.alerted_tracks = set()

    def check(self, tracked_objects):

        events = []

        if not self.is_after_hours():
            self.alerted_tracks.clear()
            return events

        current_track_ids = set()

        for tracked_object in tracked_objects:

            if tracked_object.detection.class_name != "person":
                continue

            track_id = tracked_object.track_id
            current_track_ids.add(track_id)

            if track_id in self.alerted_tracks:
                continue

            self.alerted_tracks.add(track_id)

            events.append({
                "track_id": track_id,
                "event_type": "after_hours_activity",
                "severity": SEVERITY_CRITICAL,
                "message": "Person detected outside business hours",
            })

        # Forget tracks that are no longer visible so re-entry
        # can trigger a fresh alert later.
        self.alerted_tracks &= current_track_ids

        return events

    def is_after_hours(self):

        hour = datetime.now().hour

        if self.start_hour <= self.end_hour:
            return self.start_hour <= hour < self.end_hour

        # Wraps past midnight, e.g. 22 -> 6
        return hour >= self.start_hour or hour < self.end_hour

    def reset(self):

        self.alerted_tracks.clear()

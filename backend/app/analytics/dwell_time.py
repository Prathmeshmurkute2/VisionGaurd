import time

from app.core.constants import SEVERITY_WARNING


class DwellTimeDetector:
    """
    Detects loitering: a person who stays inside a zone longer than
    `dwell_seconds`. Reuses the same "inside zone" concept as the
    intrusion detector but on its own zone/threshold, since a loitering
    zone (e.g. an entrance) is usually not the same as a hard
    restricted zone.

    Fires once per continuous stay, then resets once the person leaves.
    """

    def __init__(self, zone, dwell_seconds, margin=10, max_missing_frames=15):
        """
        `zone` may be None, meaning loitering is tracked across the
        whole frame (useful when there's no specific zone configured
        yet) rather than a specific sub-region.
        """

        self.zone = zone
        self.dwell_seconds = dwell_seconds
        self.margin = margin
        self.max_missing_frames = max_missing_frames

        # track_id -> timestamp first seen inside the zone
        self.entry_times = {}

        # track_ids that have already triggered a loitering alert
        # during their current stay (avoid repeat alerts every frame)
        self.alerted_tracks = set()

        self.missing_frames = {}

    def check(self, tracked_objects):

        events = []

        current_track_ids = set()

        for tracked_object in tracked_objects:

            if tracked_object.detection.class_name != "person":
                continue

            track_id = tracked_object.track_id
            current_track_ids.add(track_id)
            self.missing_frames[track_id] = 0

            center_x, center_y = tracked_object.detection.bbox.center

            if self.is_inside(center_x, center_y):

                if track_id not in self.entry_times:
                    self.entry_times[track_id] = time.time()

                elapsed = time.time() - self.entry_times[track_id]

                if (
                    elapsed >= self.dwell_seconds
                    and track_id not in self.alerted_tracks
                ):

                    self.alerted_tracks.add(track_id)

                    events.append({
                        "track_id": track_id,
                        "event_type": "loitering",
                        "severity": SEVERITY_WARNING,
                        "message": (
                            f"Person lingering in zone for "
                            f"{int(elapsed)}s"
                        ),
                        "dwell_seconds": int(elapsed),
                    })

            else:
                self._forget(track_id)

        # Handle tracks that left the frame entirely
        stale_tracks = set(self.entry_times) - current_track_ids

        for track_id in stale_tracks:

            self.missing_frames[track_id] = (
                self.missing_frames.get(track_id, 0) + 1
            )

            if self.missing_frames[track_id] >= self.max_missing_frames:
                self._forget(track_id)

        return events

    def is_inside(self, x, y):

        if self.zone is None:
            return True

        x1, y1, x2, y2 = self.zone
        margin = self.margin

        return (
            x1 + margin <= x <= x2 - margin
            and y1 + margin <= y <= y2 - margin
        )

    def _forget(self, track_id):

        self.entry_times.pop(track_id, None)
        self.alerted_tracks.discard(track_id)
        self.missing_frames.pop(track_id, None)

    def reset(self):

        self.entry_times.clear()
        self.alerted_tracks.clear()
        self.missing_frames.clear()

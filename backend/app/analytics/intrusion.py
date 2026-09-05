class IntrusionDetector:
    """
    Detects when a tracked person enters a restricted zone.

    Uses hysteresis to prevent duplicate events caused by
    small movements around the zone boundary.
    """

    def __init__(
        self,
        zone,
        entry_margin=10,
        exit_margin=30,
        max_missing_frames=50,
    ):

        self.zone = zone

        self.entry_margin = entry_margin
        self.exit_margin = exit_margin

        self.max_missing_frames = max_missing_frames

        # Track IDs currently considered inside
        self.inside_tracks = set()

        # Consecutive missing frames
        self.missing_frames = {}

    def check(self, tracked_objects):

        events = []

        current_track_ids = set()

        for tracked_object in tracked_objects:

            track_id = tracked_object.track_id

            # Only persons
            if (
                tracked_object.detection.class_name
                != "person"
            ):
                continue

            current_track_ids.add(track_id)

            # Track is visible
            self.missing_frames[track_id] = 0

            center_x, center_y = (
                tracked_object.detection.bbox.center
            )

            # --------------------------------
            # Already inside?
            # --------------------------------

            if track_id in self.inside_tracks:

                # Only remove the track when it has
                # clearly left the larger exit zone.
                if not self.is_inside_exit_zone(
                    center_x,
                    center_y,
                ):

                    self.inside_tracks.remove(
                        track_id
                    )

                    self.missing_frames.pop(
                        track_id,
                        None,
                    )

                continue

            # --------------------------------
            # Not inside yet
            # --------------------------------

            if self.is_inside_entry_zone(
                center_x,
                center_y,
            ):

                self.inside_tracks.add(
                    track_id
                )

                events.append({
                    "track_id": track_id,
                    "event_type": "intrusion",
                    "severity": "CRITICAL",
                    "message": (
                        "Person entered "
                        "restricted zone"
                    ),
                })

        # --------------------------------
        # Handle missing tracks
        # --------------------------------

        missing_tracks = (
            self.inside_tracks - current_track_ids
        )

        for track_id in missing_tracks:

            self.missing_frames[track_id] = (
                self.missing_frames.get(
                    track_id,
                    0,
                ) + 1
            )

            if (
                self.missing_frames[track_id]
                >= self.max_missing_frames
            ):

                self.inside_tracks.remove(
                    track_id
                )

                self.missing_frames.pop(
                    track_id,
                    None,
                )

        return events

    def is_inside_entry_zone(self, x, y):

        x1, y1, x2, y2 = self.zone

        margin = self.entry_margin

        return (
            x1 + margin <= x <= x2 - margin
            and
            y1 + margin <= y <= y2 - margin
        )

    def is_inside_exit_zone(self, x, y):

        x1, y1, x2, y2 = self.zone

        margin = self.exit_margin

        return (
            x1 - margin <= x <= x2 + margin
            and
            y1 - margin <= y <= y2 + margin
        )

    def reset(self):

        self.inside_tracks.clear()
        self.missing_frames.clear()
import cv2
import numpy as np


class IntrusionDetector:
    """
    Detects when a tracked person enters a restricted zone.

    The zone is an arbitrary polygon (list of (x, y) pixel points),
    not just a rectangle - drawn by the user on the live feed and
    persisted via the /zones API. If no zone is configured, this
    detector is a no-op (returns no events) rather than erroring.

    A grace period is used because ByteTrack can temporarily
    lose a tracked object for a few frames.
    """

    def __init__(self, zone_points=None, max_missing_frames=15):

        self.max_missing_frames = max_missing_frames

        # Tracks currently inside the restricted zone
        self.inside_tracks = set()

        # Number of consecutive frames each track has been missing
        self.missing_frames = {}

        self._polygon = None
        self.set_zone(zone_points)

    def set_zone(self, zone_points):
        """
        `zone_points` is a list of (x, y) pixel tuples, or None to
        disable zone checking entirely. Called both at startup and
        live, whenever the zone is edited/saved in the UI.
        """

        if zone_points and len(zone_points) >= 3:
            self._polygon = np.array(zone_points, dtype=np.int32)
        else:
            self._polygon = None

        # A new/changed zone invalidates any in-progress tracking
        # state from the old shape.
        self.inside_tracks.clear()
        self.missing_frames.clear()

    def has_zone(self):
        return self._polygon is not None

    @property
    def zone_points(self):
        """
        The current zone polygon as a list of (x, y) pixel points,
        or None if no zone is configured. Used by the frame drawing
        code to overlay the zone on the live stream.
        """

        if self._polygon is None:
            return None

        return self._polygon.tolist()

    def check(self, tracked_objects):

        events = []

        if self._polygon is None:
            return events

        current_track_ids = set()

        for tracked_object in tracked_objects:

            track_id = tracked_object.track_id

            # Only detect persons
            if tracked_object.detection.class_name != "person":
                continue

            current_track_ids.add(track_id)

            # Track is visible again
            self.missing_frames[track_id] = 0

            center_x, center_y = (
                tracked_object.detection.bbox.center
            )

            inside = self.is_inside(
                center_x,
                center_y,
            )

            # --------------------------------
            # Person entered restricted zone
            # --------------------------------

            if (
                inside
                and track_id not in self.inside_tracks
            ):

                self.inside_tracks.add(track_id)

                events.append({
                    "track_id": track_id,
                    "event_type": "intrusion",
                    "severity": "CRITICAL",
                    "message": "Person entered restricted zone",
                })

            # --------------------------------
            # Person left restricted zone
            # --------------------------------

            elif (
                not inside
                and track_id in self.inside_tracks
            ):

                self.inside_tracks.remove(track_id)

                self.missing_frames.pop(
                    track_id,
                    None,
                )

        # --------------------------------
        # Handle temporarily missing tracks
        # --------------------------------

        missing_tracks = (
            self.inside_tracks - current_track_ids
        )

        for track_id in missing_tracks:

            self.missing_frames[track_id] = (
                self.missing_frames.get(track_id, 0)
                + 1
            )

            # Only forget the track after the
            # grace period has expired.
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

    def is_inside(self, x, y):

        if self._polygon is None:
            return False

        result = cv2.pointPolygonTest(
            self._polygon,
            (float(x), float(y)),
            False,
        )

        return result >= 0

    def reset(self):
        """
        Clears all tracking state.
        Called when the camera starts a new session.
        """

        self.inside_tracks.clear()
        self.missing_frames.clear()

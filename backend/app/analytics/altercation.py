import time
from itertools import combinations

from app.core.constants import SEVERITY_WARNING


class AltercationDetector:
    """
    Heuristic "possible altercation" detector.

    This is NOT true violence/action detection - plain object
    detection can't tell a hug from a punch. It's a proxy: flags
    when two people are very close together AND at least one of
    them just moved unusually fast (a struggle, a shove, someone
    recoiling). It WILL false-positive on things like dancing,
    hugging, or sports, and it WILL miss attacks where neither
    person moves fast (e.g. a static grab). Treat alerts from this
    as "worth a human glance", not "confirmed incident".

    For real behavior recognition, this needs to be replaced/backed
    by a model trained on video clips for action recognition (e.g.
    a violence-detection dataset like RWF-2000), since that's a
    fundamentally different kind of model than object detection -
    it reasons over a short window of frames, not a single frame.
    """

    def __init__(
        self,
        proximity_px,
        speed_threshold,
        cooldown_seconds=8,
    ):

        self.proximity_px = proximity_px
        self.speed_threshold = speed_threshold
        self.cooldown_seconds = cooldown_seconds

        # track_id -> (x, y, timestamp) of last position
        self.last_position = {}

        # frozenset({track_id_a, track_id_b}) -> last alert timestamp
        self.last_alert_time = {}

    def check(self, tracked_objects):

        events = []
        now = time.time()

        people = [
            obj for obj in tracked_objects
            if obj.detection.class_name == "person"
        ]

        # Update speed for every visible person first.
        speeds = {}

        for person in people:

            track_id = person.track_id
            x, y = person.detection.bbox.center

            previous = self.last_position.get(track_id)
            self.last_position[track_id] = (x, y, now)

            if previous is None:
                speeds[track_id] = 0.0
                continue

            prev_x, prev_y, prev_time = previous
            dt = now - prev_time

            speeds[track_id] = (
                ((x - prev_x) ** 2 + (y - prev_y) ** 2) ** 0.5 / dt
                if dt > 0 else 0.0
            )

        # Check every pair of people currently in frame.
        for person_a, person_b in combinations(people, 2):

            id_a = person_a.track_id
            id_b = person_b.track_id

            xa, ya = person_a.detection.bbox.center
            xb, yb = person_b.detection.bbox.center

            distance = ((xa - xb) ** 2 + (ya - yb) ** 2) ** 0.5

            if distance > self.proximity_px:
                continue

            fast_movement = (
                speeds.get(id_a, 0) >= self.speed_threshold
                or speeds.get(id_b, 0) >= self.speed_threshold
            )

            if not fast_movement:
                continue

            pair_key = frozenset({id_a, id_b})
            last_alert = self.last_alert_time.get(pair_key, 0)

            if now - last_alert < self.cooldown_seconds:
                continue

            self.last_alert_time[pair_key] = now

            events.append({
                "track_id": id_a,
                "event_type": "possible_altercation",
                "severity": SEVERITY_WARNING,
                "message": (
                    "Two people in close proximity with sudden "
                    "movement - possible altercation, review footage"
                ),
                "other_track_id": id_b,
                "distance_px": round(distance, 1),
            })

        return events

    def reset(self):

        self.last_position.clear()
        self.last_alert_time.clear()

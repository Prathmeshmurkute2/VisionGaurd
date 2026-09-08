class CrowdDetector:
    """
    Detects when the number of people in the camera
    exceeds the configured crowd threshold.
    """

    def __init__(self, threshold: int = 5):
        self.threshold = threshold

        # Prevent repeated events while the crowd
        # remains above the threshold.
        self.crowd_active = False

    def check(self, tracked_objects):

        person_count = 0

        for tracked_object in tracked_objects:

            if (
                tracked_object.detection.class_name
                == "person"
            ):
                person_count += 1

        events = []

        # --------------------------------
        # Crowd detected
        # --------------------------------

        if (
            person_count >= self.threshold
            and not self.crowd_active
        ):

            self.crowd_active = True

            events.append({
                "event_type": "crowd_detected",
                "person_count": person_count,
                "severity": "WARNING",
                "message": (
                    f"Crowd detected: "
                    f"{person_count} people"
                ),
            })

        # --------------------------------
        # Crowd cleared
        # --------------------------------

        elif (
            person_count < self.threshold
            and self.crowd_active
        ):

            self.crowd_active = False

        return events

    def reset(self):
        """
        Reset crowd state when a camera session starts.
        """

        self.crowd_active = False
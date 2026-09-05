from app.core.logger import logger


class CrowdDetector:

    def __init__(
        self,
        threshold,
        clear_after_frames=20,
    ):
        self.threshold = threshold
        self.crowd_active = False
        self.below_threshold_frames = 0
        self.clear_after_frames = clear_after_frames

        def check(self, tracked_objects):

            events = []

            person_count = sum(
                1
                for tracked_object in tracked_objects
                if tracked_object.detection.class_name == "person"
            )

            logger.info(
                "CROWD STATE | people=%d | active=%s | below_frames=%d",
                person_count,
                self.crowd_active,
                self.below_threshold_frames,
            )

            if person_count >= self.threshold:

                self.below_threshold_frames = 0

                if not self.crowd_active:

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

            else:

                if self.crowd_active:

                    self.below_threshold_frames += 1

                    if (
                        self.below_threshold_frames
                        >= self.clear_after_frames
                    ):

                        self.crowd_active = False
                        self.below_threshold_frames = 0

            return events
        # rest of your existing code...
    def reset(self):
        """
        Reset crowd state for a new camera session.
        """

        self.crowd_active = False

        self.below_threshold_frames = 0
class LineCrossingDetector:
    """
    Detects when a tracked object crosses a horizontal line.
    """

    def __init__(self, line_y: float):
        self.line_y = line_y

        # Stores the previous Y position of each track
        self.previous_positions = {}

        # Stores the last known side of the line
        self.track_sides = {}
    def reset(self):
        """
        Reset tracking state for a new camera session.
        """
        self.previous_positions.clear()

    def check(self, tracked_objects):

        events = []

        for tracked_object in tracked_objects:

            track_id = tracked_object.track_id

            _, current_y = tracked_object.detection.bbox.center

            previous_y = self.previous_positions.get(track_id)

            # First time seeing this track
            if previous_y is None:

                self.previous_positions[track_id] = current_y

                # Determine initial side
                if current_y < self.line_y:
                    self.track_sides[track_id] = "ABOVE"
                else:
                    self.track_sides[track_id] = "BELOW"

                continue

            previous_side = self.track_sides.get(track_id)

            # Current side
            if current_y < self.line_y:
                current_side = "ABOVE"
            else:
                current_side = "BELOW"

            # -------------------------------------------------
            # ABOVE -> BELOW
            # -------------------------------------------------

            if previous_side == "ABOVE" and current_side == "BELOW":

                events.append({
                    "track_id": track_id,
                    "event_type": "line_crossing",
                    "direction": "IN",
                })

            # -------------------------------------------------
            # BELOW -> ABOVE
            # -------------------------------------------------

            elif previous_side == "BELOW" and current_side == "ABOVE":

                events.append({
                    "track_id": track_id,
                    "event_type": "line_crossing",
                    "direction": "OUT",
                })

            # Update state
            self.track_sides[track_id] = current_side
            self.previous_positions[track_id] = current_y

        return events
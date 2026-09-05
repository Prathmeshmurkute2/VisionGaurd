import cv2


class Visualizer:

    def draw(
        self,
        frame,
        tracked_objects,
        restricted_zone=None,
    ):

        output = frame.copy()

        # Draw restricted zone
        if restricted_zone is not None:

            x1, y1, x2, y2 = restricted_zone

            cv2.rectangle(
                output,
                (x1, y1),
                (x2, y2),
                (0, 0, 255),
                2,
            )

            cv2.putText(
                output,
                "RESTRICTED ZONE",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )

        # Draw tracked objects
        for tracked_object in tracked_objects:

            detection = tracked_object.detection
            bbox = detection.bbox

            x1 = int(bbox.x1)
            y1 = int(bbox.y1)
            x2 = int(bbox.x2)
            y2 = int(bbox.y2)

            cv2.rectangle(
                output,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            label = (
                f"{detection.class_name} "
                f"ID:{tracked_object.track_id}"
            )

            cv2.putText(
                output,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        return output


visualizer = Visualizer()
import cv2
import numpy as np


class Visualizer:

    def draw(
        self,
        frame,
        tracked_objects,
        restricted_zone=None,
    ):

        output = frame.copy()

        # Draw restricted zone (arbitrary polygon - a numpy array of
        # (x, y) pixel points, or None if no zone is configured)
        if restricted_zone is not None and len(restricted_zone) >= 3:

            polygon = np.array(restricted_zone, dtype=np.int32)

            cv2.polylines(
                output,
                [polygon],
                isClosed=True,
                color=(0, 0, 255),
                thickness=2,
            )

            overlay = output.copy()

            cv2.fillPoly(
                overlay,
                [polygon],
                (0, 0, 255),
            )

            cv2.addWeighted(
                overlay, 0.15, output, 0.85, 0, output
            )

            label_x, label_y = polygon[0]

            cv2.putText(
                output,
                "RESTRICTED ZONE",
                (int(label_x), max(int(label_y) - 10, 20)),
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

    def draw_poses(self, frame, pose_people, activity_lookup=None):
        """
        Draws a skeleton overlay + activity label for each tracked
        person. `activity_lookup` maps track_id -> activity label
        (e.g. from ActivityClassifier.get_activity()).
        """

        from app.core.constants import (
            ACTIVITY_FALL_DOWN,
            POSE_SKELETON_EDGES,
        )

        output = frame

        activity_lookup = activity_lookup or {}

        for person in pose_people:

            activity = activity_lookup.get(person.track_id)

            color = (
                (0, 0, 255)
                if activity == ACTIVITY_FALL_DOWN
                else (255, 200, 0)
            )

            # Skeleton bones
            for start_idx, end_idx in POSE_SKELETON_EDGES:

                start_kp = person.keypoints[start_idx]
                end_kp = person.keypoints[end_idx]

                if start_kp.confidence < 0.3 or end_kp.confidence < 0.3:
                    continue

                cv2.line(
                    output,
                    (int(start_kp.x), int(start_kp.y)),
                    (int(end_kp.x), int(end_kp.y)),
                    color,
                    2,
                )

            # Keypoint dots
            for keypoint in person.keypoints:

                if keypoint.confidence < 0.3:
                    continue

                cv2.circle(
                    output,
                    (int(keypoint.x), int(keypoint.y)),
                    3,
                    color,
                    -1,
                )

            # Activity label above the head
            if activity:

                label_x = int(person.bbox.x1)
                label_y = int(person.bbox.y1) - 15

                cv2.putText(
                    output,
                    activity.upper().replace("_", " "),
                    (label_x, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2,
                )

        return output


visualizer = Visualizer()
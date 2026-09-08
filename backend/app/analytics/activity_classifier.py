import math
import time

from app.core.constants import (
    ACTIVITY_FALL_DOWN,
    ACTIVITY_SITTING,
    ACTIVITY_STANDING,
    ACTIVITY_UNKNOWN,
    ACTIVITY_WALKING,
    KEYPOINT_LEFT_ANKLE,
    KEYPOINT_LEFT_HIP,
    KEYPOINT_LEFT_KNEE,
    KEYPOINT_LEFT_SHOULDER,
    KEYPOINT_RIGHT_ANKLE,
    KEYPOINT_RIGHT_HIP,
    KEYPOINT_RIGHT_KNEE,
    KEYPOINT_RIGHT_SHOULDER,
    SEVERITY_WARNING,
)

MIN_KEYPOINT_CONFIDENCE = 0.3

# Torso more than this many degrees from vertical reads as "lying down"
FALL_TORSO_ANGLE_DEG = 55

# Knee angle below this reads as "bent" (sitting); above reads as "straight"
SITTING_KNEE_ANGLE_DEG = 140

# Centroid speed above this (px/sec), combined with a standing
# posture, reads as "walking" rather than "standing still"
WALKING_SPEED_THRESHOLD = 40.0


def _get_point(keypoints, index):

    kp = keypoints[index]

    if kp.confidence < MIN_KEYPOINT_CONFIDENCE:
        return None

    return (kp.x, kp.y)


def _midpoint(a, b):

    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


def _angle_from_vertical(vector):
    """Angle in degrees between `vector` and straight-down (0, 1)."""

    vx, vy = vector
    magnitude = math.hypot(vx, vy)

    if magnitude == 0:
        return 0.0

    # cos(theta) between vector and (0, 1)
    cos_theta = vy / magnitude
    cos_theta = max(-1.0, min(1.0, cos_theta))

    return math.degrees(math.acos(cos_theta))


def _joint_angle(a, joint, b):
    """Angle in degrees at `joint`, between rays joint->a and joint->b."""

    v1 = (a[0] - joint[0], a[1] - joint[1])
    v2 = (b[0] - joint[0], b[1] - joint[1])

    dot = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = math.hypot(*v1)
    mag2 = math.hypot(*v2)

    if mag1 == 0 or mag2 == 0:
        return 180.0

    cos_theta = max(-1.0, min(1.0, dot / (mag1 * mag2)))

    return math.degrees(math.acos(cos_theta))


def classify_pose(keypoints):
    """
    Geometric rule-based activity classification from a single
    frame's keypoints: standing / sitting / walking(-ish, see note
    below) / fall_down / unknown.

    NOTE: this function alone can't distinguish "standing" from
    "walking" - that needs motion across frames, which is handled
    by ActivityClassifier.check() below. This returns a "posture"
    of either ACTIVITY_STANDING or ACTIVITY_SITTING for the
    upright case, which the caller may upgrade to ACTIVITY_WALKING
    based on movement.

    This is a heuristic, not a trained classifier - it will
    misclassify unusual poses (crouching, stretching, sitting on
    the floor cross-legged) and depends on the pose model finding
    clear shoulder/hip/knee keypoints. Swapping in a model trained
    directly on these activity classes (see the module docstring in
    detection/pose.py) will be more accurate; this keeps the
    project functional in the meantime.
    """

    left_shoulder = _get_point(keypoints, KEYPOINT_LEFT_SHOULDER)
    right_shoulder = _get_point(keypoints, KEYPOINT_RIGHT_SHOULDER)
    left_hip = _get_point(keypoints, KEYPOINT_LEFT_HIP)
    right_hip = _get_point(keypoints, KEYPOINT_RIGHT_HIP)

    if not (left_shoulder or right_shoulder) or not (left_hip or right_hip):
        return ACTIVITY_UNKNOWN

    shoulder = (
        _midpoint(left_shoulder, right_shoulder)
        if left_shoulder and right_shoulder
        else (left_shoulder or right_shoulder)
    )

    hip = (
        _midpoint(left_hip, right_hip)
        if left_hip and right_hip
        else (left_hip or right_hip)
    )

    torso_vector = (hip[0] - shoulder[0], hip[1] - shoulder[1])
    torso_angle = _angle_from_vertical(torso_vector)

    if torso_angle >= FALL_TORSO_ANGLE_DEG:
        return ACTIVITY_FALL_DOWN

    # Torso is upright - check leg bend to tell standing from sitting
    knee_angles = []

    left_knee = _get_point(keypoints, KEYPOINT_LEFT_KNEE)
    left_ankle = _get_point(keypoints, KEYPOINT_LEFT_ANKLE)

    if left_hip and left_knee and left_ankle:
        knee_angles.append(_joint_angle(left_hip, left_knee, left_ankle))

    right_knee = _get_point(keypoints, KEYPOINT_RIGHT_KNEE)
    right_ankle = _get_point(keypoints, KEYPOINT_RIGHT_ANKLE)

    if right_hip and right_knee and right_ankle:
        knee_angles.append(_joint_angle(right_hip, right_knee, right_ankle))

    if not knee_angles:
        # Legs not visible (e.g. cropped/occluded) - fall back to
        # "standing" since torso is upright and that's the safer
        # default for a security context (won't suppress a real
        # fall alert next frame, and won't wrongly flag loitering
        # as sitting).
        return ACTIVITY_STANDING

    average_knee_angle = sum(knee_angles) / len(knee_angles)

    if average_knee_angle < SITTING_KNEE_ANGLE_DEG:
        return ACTIVITY_SITTING

    return ACTIVITY_STANDING


class ActivityClassifier:
    """
    Wraps classify_pose() with per-track history so it can:
      - upgrade "standing" to "walking" based on movement over time
      - emit a debounced fall_down ALERT (not just a label) when a
        person transitions into a fall
      - expose the latest activity per track_id for the video
        overlay (see VideoService/Visualizer)
    """

    def __init__(self, cooldown_seconds=10):

        self.cooldown_seconds = cooldown_seconds

        # track_id -> (x, y, timestamp) of last position
        self.last_position = {}

        # track_id -> last emitted fall alert timestamp
        self.last_fall_alert = {}

        # track_id -> current activity label (for the frame overlay)
        self.latest_activity = {}

    def check(self, pose_people):

        events = []
        now = time.time()

        current_track_ids = set()

        for person in pose_people:

            track_id = person.track_id
            current_track_ids.add(track_id)

            posture = classify_pose(person.keypoints)

            center_x = (person.bbox.x1 + person.bbox.x2) / 2
            center_y = (person.bbox.y1 + person.bbox.y2) / 2

            previous = self.last_position.get(track_id)
            self.last_position[track_id] = (center_x, center_y, now)

            activity = posture

            if posture == ACTIVITY_STANDING and previous is not None:

                prev_x, prev_y, prev_time = previous
                dt = now - prev_time

                if dt > 0:

                    speed = (
                        ((center_x - prev_x) ** 2 + (center_y - prev_y) ** 2)
                        ** 0.5 / dt
                    )

                    if speed >= WALKING_SPEED_THRESHOLD:
                        activity = ACTIVITY_WALKING

            self.latest_activity[track_id] = activity

            if activity == ACTIVITY_FALL_DOWN:

                last_alert = self.last_fall_alert.get(track_id, 0)

                if now - last_alert >= self.cooldown_seconds:

                    self.last_fall_alert[track_id] = now

                    events.append({
                        "track_id": track_id,
                        "event_type": "fall_down",
                        "severity": SEVERITY_WARNING,
                        "message": (
                            "Pose analysis indicates a person has "
                            "fallen down - review footage"
                        ),
                    })

        # Clean up tracks that left the frame
        stale = set(self.latest_activity) - current_track_ids

        for track_id in stale:
            self.latest_activity.pop(track_id, None)
            self.last_position.pop(track_id, None)
            self.last_fall_alert.pop(track_id, None)

        return events

    def get_activity(self, track_id):
        return self.latest_activity.get(track_id)

    def reset(self):
        self.last_position.clear()
        self.last_fall_alert.clear()
        self.latest_activity.clear()

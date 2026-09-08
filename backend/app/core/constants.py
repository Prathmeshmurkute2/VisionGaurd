FRAME_BOUNDARY = b"--frame"

JPEG_CONTENT_TYPE = b"Content-Type: image/jpeg\r\n\r\n"

DEFAULT_SKIP_FRAMES = 2

MAX_RECENT_EVENTS = 10

DEFAULT_PAGE_SIZE = 20

FRAME_SKIP = 2

# --- Severity levels ---

SEVERITY_CRITICAL = "CRITICAL"
SEVERITY_WARNING = "WARNING"
SEVERITY_INFO = "INFO"

# --- Threat object classes ---
# The stock YOLO/COCO weights (yolo11n.pt) do NOT include these classes -
# COCO's 80 classes cover everyday objects, not weapons. To actually detect
# guns/knives you must point YOLO_MODEL at a model fine-tuned on a weapon
# dataset (e.g. a custom-trained yolo11 checkpoint). Once such a model is
# loaded, any detected class matching one of these names is treated as a
# CRITICAL threat automatically - no other code changes needed.
THREAT_OBJECT_CLASSES = {
    "gun",
    "pistol",
    "rifle",
    "weapon",
    "knife",
}

# --- Pose keypoints (COCO 17-keypoint order, as used by
#     Ultralytics' yolo11n-pose.pt) ---

KEYPOINT_NOSE = 0
KEYPOINT_LEFT_EYE = 1
KEYPOINT_RIGHT_EYE = 2
KEYPOINT_LEFT_EAR = 3
KEYPOINT_RIGHT_EAR = 4
KEYPOINT_LEFT_SHOULDER = 5
KEYPOINT_RIGHT_SHOULDER = 6
KEYPOINT_LEFT_ELBOW = 7
KEYPOINT_RIGHT_ELBOW = 8
KEYPOINT_LEFT_WRIST = 9
KEYPOINT_RIGHT_WRIST = 10
KEYPOINT_LEFT_HIP = 11
KEYPOINT_RIGHT_HIP = 12
KEYPOINT_LEFT_KNEE = 13
KEYPOINT_RIGHT_KNEE = 14
KEYPOINT_LEFT_ANKLE = 15
KEYPOINT_RIGHT_ANKLE = 16

# Bone connections for drawing a skeleton overlay
POSE_SKELETON_EDGES = [
    (KEYPOINT_LEFT_SHOULDER, KEYPOINT_RIGHT_SHOULDER),
    (KEYPOINT_LEFT_SHOULDER, KEYPOINT_LEFT_ELBOW),
    (KEYPOINT_LEFT_ELBOW, KEYPOINT_LEFT_WRIST),
    (KEYPOINT_RIGHT_SHOULDER, KEYPOINT_RIGHT_ELBOW),
    (KEYPOINT_RIGHT_ELBOW, KEYPOINT_RIGHT_WRIST),
    (KEYPOINT_LEFT_SHOULDER, KEYPOINT_LEFT_HIP),
    (KEYPOINT_RIGHT_SHOULDER, KEYPOINT_RIGHT_HIP),
    (KEYPOINT_LEFT_HIP, KEYPOINT_RIGHT_HIP),
    (KEYPOINT_LEFT_HIP, KEYPOINT_LEFT_KNEE),
    (KEYPOINT_LEFT_KNEE, KEYPOINT_LEFT_ANKLE),
    (KEYPOINT_RIGHT_HIP, KEYPOINT_RIGHT_KNEE),
    (KEYPOINT_RIGHT_KNEE, KEYPOINT_RIGHT_ANKLE),
]

# --- Activity labels ---

ACTIVITY_STANDING = "standing"
ACTIVITY_SITTING = "sitting"
ACTIVITY_WALKING = "walking"
ACTIVITY_FALL_DOWN = "fall_down"
ACTIVITY_UNKNOWN = "unknown"

# --- Camera ---
# Single hardcoded camera for now (see services/video_service.py).
# Kept here (not on VideoService) so other modules can reference it
# without needing to import - and thereby fully load - the video
# pipeline (YOLO/pose models) just to compare an id.
DEFAULT_CAMERA_ID = "Gate-1"
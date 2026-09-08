from ultralytics import YOLO

from app.core.logger import logger


class PoseDetector:
    """
    Loads a YOLO pose-estimation model (17 COCO keypoints per person).

    This ships pretrained from Ultralytics - no training needed to
    get skeleton keypoints. What IS built on top (standing/sitting/
    walking/fall-down classification) is our own geometric heuristic
    for now (see analytics/activity_classifier.py); swapping in a
    model fine-tuned specifically for those activity classes later
    just means pointing POSE_MODEL at that checkpoint and replacing
    the classifier's logic - the rest of the pipeline (tracking,
    events, alerts) stays the same.
    """

    def __init__(self, model_path: str = "yolo11n-pose.pt"):
        logger.info("Loading pose model...")
        self.model = YOLO(model_path)
        logger.info("Pose model loaded successfully!")

    def get_model(self):
        return self.model


pose_detector = PoseDetector()

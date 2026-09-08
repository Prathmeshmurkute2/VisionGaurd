import cv2
import time
import asyncio
from datetime import datetime

from app.core.config import settings
from app.core.logger import logger
from app.core.constants import DEFAULT_CAMERA_ID

from app.analytics.intrusion import IntrusionDetector

from app.tracking.tracker import tracker
from app.utils.visualizer import visualizer

from app.services.metrics_service import metrics_service
from app.services.event_service import event_service

from app.analytics.line_crossing import LineCrossingDetector

from app.schemas.event import Event

from app.database.session import SessionLocal

from app.analytics.crowd_detector import CrowdDetector
from app.analytics.dwell_time import DwellTimeDetector
from app.analytics.motion import RunningDetector
from app.analytics.after_hours import AfterHoursDetector
from app.analytics.threat_object import ThreatObjectDetector
from app.analytics.fire_detector import FireDetector
from app.analytics.altercation import AltercationDetector
from app.analytics.fall_detector import FallDetector
from app.analytics.activity_classifier import ActivityClassifier
from app.tracking.pose_tracker import pose_tracker
from app.repositories.zone_repository import zone_repository

class VideoService:
    """
    Handles video capture, object tracking,
    analytics, visualization and frame streaming.
    """

    CAMERA_ID = DEFAULT_CAMERA_ID

    def __init__(self):
        self.cap = None
        self.is_running = False

        self.frame_width = None
        self.frame_height = None

        self.line_crossing_detector = LineCrossingDetector(
            line_y=400
        )

        # No hardcoded zone anymore - loaded from the database
        # (see load_intrusion_zone()) once the camera starts, and
        # kept live-updatable via update_intrusion_zone().
        self.intrusion_detector = IntrusionDetector(
            zone_points=None
        )

        self.processing_fps = settings.PROCESSING_FPS
        self.frame_interval = 1.0 / self.processing_fps
        self.last_processed_time = 0.0

        self.crowd_detector = CrowdDetector(
            threshold=settings.CROWD_THRESHOLD
        )

        # --- Suspicious activity detectors ---

        self.dwell_time_detector = DwellTimeDetector(
            zone=None,  # whole frame; no dedicated loitering zone yet
            dwell_seconds=settings.LOITERING_SECONDS,
        )

        self.running_detector = RunningDetector(
            speed_threshold=settings.RUNNING_SPEED_THRESHOLD,
        )

        self.after_hours_detector = AfterHoursDetector(
            start_hour=settings.AFTER_HOURS_START_HOUR,
            end_hour=settings.AFTER_HOURS_END_HOUR,
        )

        self.threat_object_detector = ThreatObjectDetector()

        self.fire_detector = FireDetector()

        self.altercation_detector = AltercationDetector(
            proximity_px=settings.ALTERCATION_PROXIMITY_PX,
            speed_threshold=settings.ALTERCATION_SPEED_THRESHOLD,
        )

        self.fall_detector = FallDetector(
            window_seconds=settings.FALL_WINDOW_SECONDS,
        )

        # Pose-based activity recognition (standing/sitting/walking/
        # fall_down). When enabled, this supersedes the crude
        # bbox-aspect-ratio FallDetector above for fall alerts,
        # since keypoint geometry is much more reliable - the old
        # detector is kept as a fallback if you ever disable this.
        self.activity_recognition_enabled = (
            settings.ACTIVITY_RECOGNITION_ENABLED
        )

        self.activity_classifier = ActivityClassifier()
        self.latest_pose_people = []
    # ---------------------------------------------------------
    # VIDEO
    # ---------------------------------------------------------
    def start_camera(self, video_source=None):

        if self.is_running:
            logger.info(
                "Camera is already running."
            )
            return

        self.open_video(video_source)

        self.last_processed_time = (
            time.perf_counter()
        )

        self.is_running = True

        self.reset_analytics()

        logger.info(
            "🟢 Camera started. "
            "Processing FPS: %s",
            self.processing_fps,
        )

    def stop_camera(self):
        """
        Stops the camera and releases resources.
        """

        if not self.is_running:
            logger.info("Camera is already stopped.")
            return

        self.is_running = False

        if self.cap is not None:
            self.cap.release()
            self.cap = None

        logger.info("🔴 Camera stopped.")

    def reset_analytics(self):
        """
        Clears all stateful analytics/detector history so a fresh
        camera session doesn't inherit stale track state (e.g. a
        loitering timer that started during a previous run).
        """

        self.line_crossing_detector.previous_positions.clear()
        self.line_crossing_detector.track_sides.clear()

        self.intrusion_detector.reset()
        self.crowd_detector.reset()
        self.dwell_time_detector.reset()
        self.running_detector.reset()
        self.after_hours_detector.reset()
        self.threat_object_detector.reset()
        self.fire_detector.reset()
        self.altercation_detector.reset()
        self.fall_detector.reset()
        self.activity_classifier.reset()


    def open_video(self, video_source=None):
        """
        Opens the configured video source.
        """

        source = video_source or settings.VIDEO_SOURCE

        # Convert "0" from environment variable to integer 0
        if isinstance(source, str) and source.isdigit():
            source = int(source)

        logger.info(
            "Opening video source: %s",
            source,
        )

        self.cap = cv2.VideoCapture(source)

        logger.info(
            "Camera opened: %s",
            self.cap.isOpened(),
        )

        if not self.cap.isOpened():

            logger.error(
                "Unable to open video source: %s",
                source,
            )

            raise FileNotFoundError(
                f"Cannot open video source: {source}"
            )

        logger.info(
            "Video source opened successfully."
        )

        self.frame_width = int(
            self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0
        )

        self.frame_height = int(
            self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0
        )

        # Some sources (certain webcams/streams) report 0 for these
        # properties until a frame has actually been read - grab
        # one to get real dimensions in that case.
        if not self.frame_width or not self.frame_height:

            ok, probe_frame = self.cap.read()

            if ok:
                self.frame_height, self.frame_width = probe_frame.shape[:2]

                # Rewind so this frame still gets processed normally
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        self.load_intrusion_zone()

    def load_intrusion_zone(self):
        """
        Loads the active intrusion zone for this camera from the
        database and applies it to the running detector, converting
        the stored normalized (0.0-1.0) points to pixel coordinates
        for the current video resolution.
        """

        if not self.frame_width or not self.frame_height:
            logger.warning(
                "Frame dimensions unknown - skipping zone load."
            )
            return

        db = SessionLocal()

        try:

            db_zone = zone_repository.get_active_by_camera(
                db, self.CAMERA_ID, zone_type="intrusion"
            )

            if db_zone is None:
                self.intrusion_detector.set_zone(None)
                return

            pixel_points = [
                (
                    point["x"] * self.frame_width,
                    point["y"] * self.frame_height,
                )
                for point in db_zone.points
            ]

            self.intrusion_detector.set_zone(pixel_points)

            logger.info(
                "Loaded intrusion zone '%s' (%d points).",
                db_zone.name,
                len(pixel_points),
            )

        finally:
            db.close()

    def update_intrusion_zone(self, normalized_points):
        """
        Live-updates the running intrusion zone without needing to
        restart the camera - called right after a zone is
        created/edited via the /zones API for this camera.

        `normalized_points` is a list of {"x": float, "y": float}
        (or None to clear the zone), each in the 0.0-1.0 range.
        """

        if not normalized_points:
            self.intrusion_detector.set_zone(None)
            return

        if not self.frame_width or not self.frame_height:
            logger.warning(
                "Frame dimensions unknown - cannot apply zone "
                "update until the camera has started at least once."
            )
            return

        pixel_points = [
            (
                point["x"] * self.frame_width,
                point["y"] * self.frame_height,
            )
            for point in normalized_points
        ]

        self.intrusion_detector.set_zone(pixel_points)

    def read_frame(self):
        """
        Reads the next frame.
        """

        if self.cap is None:
            return False, None

        return self.cap.read()

    # ---------------------------------------------------------
    # AI PIPELINE
    # ---------------------------------------------------------

    def process_frame(self, frame):
        """
        Runs the complete AI pipeline.

        Pipeline:

        Frame
          ↓
        YOLO + ByteTrack
          ↓
        Tracked Objects
          ↓
        Analytics
          ↓
        Visualization
        """

        # -----------------------------------------------------
        # 1. YOLO + ByteTrack
        # -----------------------------------------------------

        tracked_objects = tracker.track(frame)

        logger.debug(
            "Tracked objects: %d",
            len(tracked_objects),
        )

        # -----------------------------------------------------
        # 1b. Pose estimation (for activity recognition)
        # -----------------------------------------------------

        pose_people = []

        if self.activity_recognition_enabled:
            pose_people = pose_tracker.track(frame)

        self.latest_pose_people = pose_people

        # -----------------------------------------------------
        # 2. Metrics
        # -----------------------------------------------------

        metrics_service.processed_frames += 1

        metrics_service.detected_objects += len(
            tracked_objects
        )

        metrics_service.update_fps()

        # -----------------------------------------------------
        # 3. Analytics
        # -----------------------------------------------------

        events = self.process_analytics(
            tracked_objects,
            frame,
            pose_people,
        )

        # -----------------------------------------------------
        # 4. Log detected events
        # -----------------------------------------------------

        if events:

            logger.info(
                "Analytics events detected: %s",
                events,
            )

            print(
                "🚨 EVENTS:",
                events,
            )

        # -----------------------------------------------------
        # 5. Draw detections
        # -----------------------------------------------------

        output = self.draw_frame(
            frame,
            tracked_objects,
        )

        if self.activity_recognition_enabled and pose_people:

            output = visualizer.draw_poses(
                output,
                pose_people,
                self.activity_classifier.latest_activity,
            )

        return output

    # ---------------------------------------------------------
    # ANALYTICS + EVENT CREATION
    # ---------------------------------------------------------

    def process_analytics(self, tracked_objects, frame=None, pose_people=None):

        analytics_events = []

        # --------------------------------
        # Line crossing
        # --------------------------------

        line_events = self.line_crossing_detector.check(
            tracked_objects
        )

        analytics_events.extend(
            line_events
        )

        # --------------------------------
        # Intrusion (restricted zone)
        # --------------------------------

        intrusion_events = self.intrusion_detector.check(
            tracked_objects
        )

        analytics_events.extend(
            intrusion_events
        )

        # --------------------------------
        # Crowd detection
        # --------------------------------

        crowd_events = self.crowd_detector.check(
            tracked_objects
        )

        analytics_events.extend(
            crowd_events
        )

        # --------------------------------
        # Loitering (dwell time)
        # --------------------------------

        loitering_events = self.dwell_time_detector.check(
            tracked_objects
        )

        analytics_events.extend(
            loitering_events
        )

        # --------------------------------
        # Fast movement / running
        # --------------------------------

        running_events = self.running_detector.check(
            tracked_objects
        )

        analytics_events.extend(
            running_events
        )

        # --------------------------------
        # After-hours activity
        # --------------------------------

        after_hours_events = self.after_hours_detector.check(
            tracked_objects
        )

        analytics_events.extend(
            after_hours_events
        )

        # --------------------------------
        # Threat objects (weapons)
        # --------------------------------

        threat_events = self.threat_object_detector.check(
            tracked_objects
        )

        analytics_events.extend(
            threat_events
        )

        # --------------------------------
        # Possible altercation (proximity + sudden movement)
        # --------------------------------

        altercation_events = self.altercation_detector.check(
            tracked_objects
        )

        analytics_events.extend(
            altercation_events
        )

        # --------------------------------
        # Fall detection - pose-based (preferred) or bbox heuristic
        # --------------------------------

        if self.activity_recognition_enabled:

            fall_events = self.activity_classifier.check(
                pose_people or []
            )

        else:

            fall_events = self.fall_detector.check(
                tracked_objects
            )

        analytics_events.extend(
            fall_events
        )

        # --------------------------------
        # Fire / flame (heuristic)
        # --------------------------------

        if frame is not None and settings.FIRE_DETECTION_ENABLED:

            fire_events = self.fire_detector.check(frame)

            analytics_events.extend(
                fire_events
            )

        # --------------------------------
        # Create database events
        # --------------------------------

        if not analytics_events:
            return []

        logger.info(
            "Analytics events detected: %s",
            analytics_events,
        )

        db = SessionLocal()

        try:

            for analytics_event in analytics_events:

                event = Event(
                    event_type=analytics_event["event_type"],
                    track_id=analytics_event.get(
                        "track_id",
                        0,
                    ),
                    camera_id=self.CAMERA_ID,
                    timestamp=datetime.now(),
                    severity=analytics_event.get(
                        "severity",
                        "INFO",
                    ),
                    message=analytics_event.get(
                        "message",
                        analytics_event["event_type"].replace("_", " ").title(),
                    ),
                    metadata={
                        key: value
                        for key, value
                        in analytics_event.items()
                        if key not in {
                            "event_type",
                            "track_id",
                            "severity",
                            "message",
                        }
                    },
                )

                event_response = event_service.create_event(
                    db=db,
                    event=event,
                )

                logger.info(
                    "🚨 Event created successfully: %s",
                    event_response,
                )

        except Exception:

            logger.exception(
                "Failed to create surveillance event."
            )

        finally:

            db.close()

        return analytics_events
    # ---------------------------------------------------------
    # VISUALIZATION
    # ---------------------------------------------------------

    def draw_frame(
        self,
        frame,
        tracked_objects,
    ):
        """
        Draws bounding boxes, IDs and analytics.
        """

        return visualizer.draw(
            frame,
            tracked_objects,
            restricted_zone=self.intrusion_detector.zone_points,
        )

    # ---------------------------------------------------------
    # ENCODING
    # ---------------------------------------------------------

    def encode_frame(self, frame):
        """
        Converts frame into JPEG bytes.
        """

        success, buffer = cv2.imencode(
            ".jpg",
            frame,
        )

        if not success:

            logger.warning(
                "Failed to encode frame."
            )

            return None

        return buffer.tobytes()

    # ---------------------------------------------------------
    # DESKTOP DISPLAY
    # ---------------------------------------------------------

    def display_frame(self, frame):
        """
        Displays frame using OpenCV.
        """

        cv2.namedWindow(
            "Intelligent Video Surveillance",
            cv2.WINDOW_NORMAL,
        )

        cv2.resizeWindow(
            "Intelligent Video Surveillance",
            1280,
            720,
        )

        cv2.imshow(
            "Intelligent Video Surveillance",
            frame,
        )

    # ---------------------------------------------------------
    # CLEANUP
    # ---------------------------------------------------------

    def cleanup(self):
        """
        Releases all resources.
        """

        if self.cap is not None:

            self.cap.release()

            self.cap = None

        cv2.destroyAllWindows()

        logger.info(
            "Video resources released."
        )

    # ---------------------------------------------------------
    # DESKTOP VIDEO PROCESSING
    # ---------------------------------------------------------

    def process_video(self, video_source=None):
        """
        Runs desktop OpenCV preview.
        """

        self.open_video(video_source)

        try:

            while True:

                success, frame = self.read_frame()

                if not success:
                    break

                output = self.process_frame(
                    frame
                )

                self.display_frame(
                    output
                )

                if (
                    cv2.waitKey(1) & 0xFF
                    == ord("q")
                ):
                    break

        finally:

            self.cleanup()

    # ---------------------------------------------------------
    # FASTAPI STREAMING
    # ---------------------------------------------------------

    def generate_frames(self):
        """
        Streams processed frames while the camera is running.

        Camera may provide frames faster than the AI pipeline
        should process them. YOLO + ByteTrack are therefore
        limited by PROCESSING_FPS.
        """

        try:

            while self.is_running:

                success, frame = self.read_frame()

                if not success:
                    logger.warning(
                        "Failed to read frame."
                    )
                    break

                current_time = time.perf_counter()

                # --------------------------------
                # FPS throttling
                # --------------------------------

                elapsed = (
                    current_time
                    - self.last_processed_time
                )

                if elapsed < self.frame_interval:

                    continue

                self.last_processed_time = current_time

                # --------------------------------
                # AI processing
                # --------------------------------

                output = self.process_frame(frame)

                frame_bytes = self.encode_frame(
                    output
                )

                if frame_bytes is None:
                    continue

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + frame_bytes
                    + b"\r\n"
                )

        finally:

            logger.info(
                "Frame generator stopped."
            )

video_service = VideoService()
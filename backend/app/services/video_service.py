import cv2
import time

from datetime import datetime
from app.websocket.publisher import event_publisher

from app.core.config import settings
from app.core.logger import logger

from app.analytics.intrusion import IntrusionDetector

from app.tracking.tracker import tracker
from app.utils.visualizer import visualizer

from app.services.metrics_service import metrics_service
from app.services.event_service import event_service

from app.analytics.line_crossing import LineCrossingDetector

from app.schemas.event import Event

from app.database.session import SessionLocal

from app.analytics.crowd_detector import CrowdDetector

class VideoService:
    """
    Handles video capture, object tracking,
    analytics, visualization and frame streaming.
    """

    def __init__(self):
        self.cap = None
        self.is_running = False

        self.line_crossing_detector = LineCrossingDetector(
            line_y=400
        )

        self.intrusion_detector = IntrusionDetector(
            zone=(400, 200, 900, 600)
        )

        self.processing_fps = settings.PROCESSING_FPS
        self.frame_interval = 1.0 / self.processing_fps
        self.last_processed_time = 0.0

        self.crowd_detector = CrowdDetector(
            threshold=settings.CROWD_THRESHOLD
        )
    # ---------------------------------------------------------
    # VIDEO
    # ---------------------------------------------------------
    def start_camera(self, video_source=None):

        if self.is_running:
            logger.info(
                "Camera is already running."
            )
            return

        # Reset analytics state for new session
        self.line_crossing_detector.reset()
        self.intrusion_detector.reset()
        self.crowd_detector.reset()

        self.open_video(video_source)

        self.last_processed_time = (
            time.perf_counter()
        )

        self.is_running = True

        logger.info(
            "🟢 Camera started. Processing FPS: %s",
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
            tracked_objects
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

        return output

    # ---------------------------------------------------------
    # ANALYTICS + EVENT CREATION
    # ---------------------------------------------------------

    def process_analytics(self, tracked_objects):

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
        # Intrusion
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
                    camera_id="Gate-1",
                    timestamp=datetime.now(),
                    severity=analytics_event.get(
                        "severity",
                        "INFO",
                    ),

                    message=analytics_event.get(
                        "message",
                        f"{analytics_event['event_type']} detected",
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
            restricted_zone=self.intrusion_detector.zone,
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
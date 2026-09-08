from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "Intelligent Video Surveillance System"

    APP_VERSION: str = "1.0.0"

    VIDEO_SOURCE: str = "0"

    YOLO_MODEL: str = "yolov8n.pt"

    CONFIDENCE_THRESHOLD: float = 0.5

    DATABASE_URL: str

    PROCESSING_FPS: int = 10

    CROWD_THRESHOLD: int = 5

    JWT_SECRET_KEY: str = "change-this-secret-key-in-production"

    JWT_ALGORITHM: str = "HS256"

    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- Suspicious activity detection ---

    LOITERING_SECONDS: int = 30
    """How long a person must stay in the loitering zone before an alert fires."""

    RUNNING_SPEED_THRESHOLD: float = 250.0
    """Pixels/second of centroid movement above which a person is flagged as running."""

    AFTER_HOURS_START_HOUR: int = 22
    """Hour (0-23) after which activity is considered after-hours."""

    AFTER_HOURS_END_HOUR: int = 6
    """Hour (0-23) before which activity is considered after-hours."""

    FIRE_DETECTION_ENABLED: bool = True

    ALTERCATION_PROXIMITY_PX: float = 150.0
    ALTERCATION_SPEED_THRESHOLD: float = 200.0

    FALL_WINDOW_SECONDS: float = 1.5

    ACTIVITY_RECOGNITION_ENABLED: bool = True
    POSE_MODEL: str = "yolo11n-pose.pt"

    # --- Alert delivery ---

    ALERT_EMAIL_ENABLED: bool = False
    ALERT_EMAIL_MIN_SEVERITY: str = "CRITICAL"
    ALERT_EMAIL_TO: str = ""
    ALERT_EMAIL_FROM: str = ""

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
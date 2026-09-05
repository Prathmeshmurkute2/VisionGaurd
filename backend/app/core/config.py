from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "Intelligent Video Surveillance System"

    APP_VERSION: str = "1.0.0"

    VIDEO_SOURCE: str = "0"

    YOLO_MODEL: str = "yolov8n.pt"

    CONFIDENCE_THRESHOLD: float = 0.5

    DATABASE_URL: str

    PROCESSING_FPS: int = 10

    CROWD_THRESHOLD: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
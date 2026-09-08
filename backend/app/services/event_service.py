from sqlalchemy.orm import Session

from app.repositories.event_repository import event_repository
from app.schemas.event import Event
from app.schemas.event_response import EventResponse
from app.websocket.publisher import event_publisher
from app.services.notification_service import notification_service


class EventService:

    def create_event(
        self,
        db: Session,
        event: Event,
    ):

        # 1. Save event to database
        db_event = event_repository.create(
            db=db,
            event=event,
        )

        # 2. Convert DB model to response schema
        event_response = EventResponse.model_validate(
            db_event
        )

        # 3. Push a live alert over WebSocket to connected dashboards
        event_publisher.publish_event_threadsafe(
            event_type="event_created",
            payload=event_response.model_dump(mode="json"),
        )

        # 4. Optionally email high-severity alerts
        notification_service.notify(
            event_type=event_response.event_type,
            severity=event_response.severity,
            message=event_response.message,
            camera_id=event_response.camera_id,
        )

        return event_response

    def get_events(
        self,
        db: Session,
        page: int,
        size: int,
    ):

        skip = (page - 1) * size

        events = event_repository.get_all(
            db,
            skip=skip,
            limit=size,
        )

        return [
            EventResponse.model_validate(event)
            for event in events
        ]


event_service = EventService()
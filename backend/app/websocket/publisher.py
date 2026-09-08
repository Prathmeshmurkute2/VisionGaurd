import asyncio

from app.websocket.manager import manager
from app.core.logger import logger


class EventPublisher:

    def __init__(self):
        # Captured at FastAPI startup so background threads (e.g. the
        # video processing loop, which runs synchronously in a
        # threadpool) can schedule broadcasts onto it safely.
        self.loop: asyncio.AbstractEventLoop | None = None

    def bind_loop(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop

    async def publish_event(
        self,
        event_type: str,
        payload: dict,
    ):
        message = {
            "type": event_type,
            "data": payload,
        }

        print("📡 Broadcasting:", message)

        await manager.broadcast(message)

    def publish_event_threadsafe(
        self,
        event_type: str,
        payload: dict,
    ):
        """
        Schedules publish_event() from a plain (non-async) thread,
        e.g. the synchronous video processing pipeline.
        """

        if self.loop is None:
            logger.warning(
                "EventPublisher.loop not bound yet; "
                "dropping websocket broadcast for %s",
                event_type,
            )
            return

        asyncio.run_coroutine_threadsafe(
            self.publish_event(event_type, payload),
            self.loop,
        )


event_publisher = EventPublisher()
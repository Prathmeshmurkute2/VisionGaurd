from fastapi import FastAPI
from app.api.routes.events import router as event_router
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging_middleware import LoggingMiddleware
from app.api.routes.dashboard import router as dashboard_router
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.camera import router as camera_router
from app.core.config import settings
from app.api.routes.health import router as health_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.websocket import router as websocket_router
from app.api.routes.demo import router as demo_router
from app.api.routes.auth import router as auth_router
from app.api.routes.zones import router as zone_router
from app.websocket.publisher import event_publisher

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

register_exception_handlers(app)

app.include_router(demo_router)
app.include_router(auth_router)
app.include_router(websocket_router)
app.include_router(metrics_router)
app.include_router(health_router)
app.include_router(camera_router)
app.include_router(dashboard_router)

app.include_router(event_router)
app.include_router(zone_router)

@app.on_event("startup")
async def bind_event_publisher_loop():
    import asyncio

    event_publisher.bind_loop(asyncio.get_running_loop())

@app.get("/")
def root():
    return {
        "message":"Welcome to Intelligent Video Serveillance System 🚀"
    }
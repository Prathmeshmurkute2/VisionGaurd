import smtplib
from email.message import EmailMessage

from app.core.config import settings
from app.core.constants import SEVERITY_CRITICAL, SEVERITY_WARNING
from app.core.logger import logger

# Ordered so we can compare "is this severity >= the configured minimum"
_SEVERITY_ORDER = {SEVERITY_WARNING: 1, SEVERITY_CRITICAL: 2}


class NotificationService:
    """
    Sends email alerts for high-severity surveillance events.

    Fully optional: if ALERT_EMAIL_ENABLED is False or SMTP settings
    are missing, this quietly no-ops rather than raising, so a
    misconfigured mail server never takes the surveillance pipeline
    down.
    """

    def notify(self, event_type: str, severity: str, message: str, camera_id: str):

        if not settings.ALERT_EMAIL_ENABLED:
            return

        if not self._meets_threshold(severity):
            return

        if not (settings.SMTP_HOST and settings.ALERT_EMAIL_TO):
            logger.warning(
                "ALERT_EMAIL_ENABLED is True but SMTP_HOST/ALERT_EMAIL_TO "
                "are not configured; skipping email alert."
            )
            return

        try:
            self._send(event_type, severity, message, camera_id)

        except Exception:
            # Never let an email failure break the detection pipeline.
            logger.exception("Failed to send alert email.")

    def _meets_threshold(self, severity: str) -> bool:

        minimum = _SEVERITY_ORDER.get(
            settings.ALERT_EMAIL_MIN_SEVERITY,
            _SEVERITY_ORDER[SEVERITY_CRITICAL],
        )
        current = _SEVERITY_ORDER.get(severity, 0)

        return current >= minimum

    def _send(self, event_type, severity, message, camera_id):

        email = EmailMessage()

        email["Subject"] = f"[{severity}] Surveillance alert: {event_type}"
        email["From"] = settings.ALERT_EMAIL_FROM or settings.SMTP_USER
        email["To"] = settings.ALERT_EMAIL_TO

        email.set_content(
            f"Camera: {camera_id}\n"
            f"Event: {event_type}\n"
            f"Severity: {severity}\n\n"
            f"{message}"
        )

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:

            server.starttls()

            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

            server.send_message(email)

        logger.info("Alert email sent for %s (%s)", event_type, severity)


notification_service = NotificationService()

import asyncio
import aiosmtplib
from email.message import EmailMessage

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmailSender:
    async def send_email(self, to_email: str, subject: str, html_content: str) -> None:
        """Send an HTML email via SMTP with retries."""
        if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
            logger.error("SMTP settings are incomplete, email not sent")
            return

        msg = EmailMessage()
        msg["From"] = settings.SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(html_content, subtype="html")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Determine TLS/SSL mode based on port
                start_tls = settings.SMTP_PORT == 587
                use_tls = settings.SMTP_PORT == 465
                await aiosmtplib.send(
                    msg,
                    hostname=settings.SMTP_HOST,
                    port=settings.SMTP_PORT,
                    username=settings.SMTP_USER,
                    password=settings.SMTP_PASSWORD,
                    start_tls=start_tls,
                    use_tls=use_tls,
                )
                logger.info(f"Email sent to {to_email} with subject '{subject}'")
                return
            except Exception as e:
                logger.warning(
                    f"Failed to send email (attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # exponential backoff
        logger.error(f"Failed to send email to {to_email} after {max_retries} attempts")

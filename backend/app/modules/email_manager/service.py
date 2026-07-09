from app.modules.email_manager.sender import EmailSender
from app.modules.email_manager.templates import get_verification_code_template
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmailService:
    def __init__(self, sender: EmailSender):
        self.sender = sender

    async def send_verification_code(self, email: str, code: str) -> None:
        """Send a verification code email."""
        subject = "Verification code for Tic-Tac-Toe"
        html_content = get_verification_code_template(code)
        await self.sender.send_email(email, subject, html_content)

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailClient:
    """
    A class to send emails using Gmail's SMTP server.

    Attributes:
        smtp_server (str): Gmail's SMTP server address.
        smtp_port (int): Gmail's SMTP server port.
        email (str): The sender's email address.
        password (str): The sender's email password or app password.
    """

    def __init__(self, email: str, password: str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        """
        Initialize the EmailClient.

        Args:
            email (str): The sender's email address.
            password (str): The sender's email password or app password.
            smtp_server (str, optional): SMTP server address. Defaults to "smtp.gmail.com".
            smtp_port (int, optional): SMTP server port. Defaults to 587.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = email
        self.password = password

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        is_html: bool = False,
    ) -> bool:
        """
        Send an email using Gmail's SMTP server.

        Args:
            to_emails (List[str]): List of recipient email addresses.
            subject (str): The subject of the email.
            body (str): The body of the email.
            from_email (Optional[str], optional): The sender's email address. Defaults to the email used in initialization.
            is_html (bool, optional): Whether the body is HTML. Defaults to False.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        # Use the provided "from_email" or default to the initialized email
        from_email = from_email or self.email

        # Create the email message
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = ", ".join(to_emails)
        msg["Subject"] = subject

        # Attach the body as plain text or HTML
        if is_html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        try:
            # Connect to the SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Upgrade the connection to secure
                server.login(self.email, self.password)  # Authenticate
                server.sendmail(from_email, to_emails, msg.as_string())  # Send the email

            logger.info(f"Email sent successfully to {to_emails}")
            return True
        except smtplib.SMTPException as e:
            logger.error(f"Failed to send email: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Load credentials from environment variables
    EMAIL = os.getenv("GMAIL_EMAIL")
    PASSWORD = os.getenv("GMAIL_PASSWORD")

    if not EMAIL or not PASSWORD:
        raise ValueError("Please set GMAIL_EMAIL and GMAIL_PASSWORD in the .env file.")

    # Initialize the email client
    email_client = EmailClient(email=EMAIL, password=PASSWORD)

    # Send an email
    to_emails = [EMAIL]
    subject = "Test Email"
    body = "This is a test email sent using Python."

    success = email_client.send_email(
        to_emails=[EMAIL],
        subject="Test Email",
        body="This is a test email.",
        from_email="no-reply@gmail.com",
    )

    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email.")
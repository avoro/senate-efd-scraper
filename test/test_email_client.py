import unittest
from unittest.mock import patch, MagicMock
import os
from src.email_client import EmailClient
import smtplib


class TestEmailClient(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.email = "test@example.com"
        self.password = "test_password"
        self.client = EmailClient(self.email, self.password)

    def test_init(self):
        """Test EmailClient initialization."""
        self.assertEqual(self.client.email, self.email)
        self.assertEqual(self.client.password, self.password)
        self.assertEqual(self.client.smtp_server, "smtp.gmail.com")
        self.assertEqual(self.client.smtp_port, 587)

    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending."""
        # Setup
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        # Test
        result = self.client.send_email(
            to_emails=["recipient@example.com"],
            subject="Test Subject",
            body="Test Body"
        )

        # Assert
        self.assertTrue(result)
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(self.email, self.password)
        mock_smtp_instance.sendmail.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_email_with_attachment(self, mock_smtp):
        """Test email sending with attachment."""
        # Create a temporary test file
        test_file = "test_attachment.txt"
        with open(test_file, "w") as f:
            f.write("Test content")

        try:
            # Setup
            mock_smtp_instance = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

            # Test
            result = self.client.send_email(
                to_emails=["recipient@example.com"],
                subject="Test Subject",
                body="Test Body",
                attachments=[test_file]
            )

            # Assert
            self.assertTrue(result)
            mock_smtp_instance.sendmail.assert_called_once()

        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.remove(test_file)

    @patch('smtplib.SMTP')
    def test_send_email_smtp_error(self, mock_smtp):
        """Test email sending with SMTP error."""
        # Setup
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.sendmail.side_effect = smtplib.SMTPException("Test error")
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        # Test
        result = self.client.send_email(
            to_emails=["recipient@example.com"],
            subject="Test Subject",
            body="Test Body"
        )

        # Assert
        self.assertFalse(result)

    def test_send_email_invalid_attachment(self):
        """Test email sending with invalid attachment."""
        result = self.client.send_email(
            to_emails=["recipient@example.com"],
            subject="Test Subject",
            body="Test Body",
            attachments=["nonexistent_file.txt"]
        )
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
    
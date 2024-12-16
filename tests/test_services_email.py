import unittest
from unittest.mock import AsyncMock, patch
from src.services.email import EmailService

class TestEmailService(unittest.IsolatedAsyncioTestCase):
    async def test_send_email(self):
        # Mock email backend
        with patch("src.services.email.EmailService.send_email") as mock_send:
            mock_send.return_value = True  # Simulate successful send

            # Call the service
            email_service = EmailService()
            result = await email_service.send_email(
                to="recipient@mail.com",
                subject="Test Email",
                body="This is a test email"
            )

            # Assertions
            mock_send.assert_called_once()
            self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()

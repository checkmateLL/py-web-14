import logging
from typing import Dict, Optional

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi import HTTPException
from pydantic import EmailStr

from src.conf.config import settings
from jinja2 import Environment, FileSystemLoader
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.mail_username,
            MAIL_PASSWORD=settings.mail_password,
            MAIL_FROM=settings.mail_from,
            MAIL_PORT=settings.mail_port,
            MAIL_SERVER=settings.mail_server,
            MAIL_FROM_NAME=settings.mail_from_name,
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
            TEMPLATE_FOLDER="src/services/templates"
        )
        self.logger = logging.getLogger(__name__)
        self.jinja_env = Environment(
            loader=FileSystemLoader('src/services/templates'),
            autoescape=True
        )

    async def send_email(
        self, 
        recipient: EmailStr, 
        username: str, 
        subject: str = "Notification",
        template_name: str = "email_template.html",
        template_body: Optional[Dict] = None
    ) -> bool:
        """
        Send an email with advanced error handling and Jinja2 template rendering.
        """
        try:
            # Render the template
            template = self.jinja_env.get_template(template_name)
            body = template.render(**(template_body or {"fullname": username}))

            # Create a multipart message
            message = MIMEMultipart()
            message['From'] = self.conf.MAIL_FROM
            message['To'] = recipient
            message['Subject'] = subject

            # Attach the HTML body
            message.attach(MIMEText(body, 'html'))

            # Send email using aiosmtplib for more control
            async with aiosmtplib.SMTP(
                hostname=self.conf.MAIL_SERVER, 
                port=self.conf.MAIL_PORT,
                use_tls=self.conf.MAIL_SSL_TLS
            ) as smtp:
                await smtp.login(self.conf.MAIL_USERNAME, self.conf.MAIL_PASSWORD)
                await smtp.send_message(message)

            self.logger.info(f"Email sent successfully to {recipient}")
            return True

        except Exception as e:
            self.logger.error(f"Email sending failed: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to send email: {str(e)}"
            )

    async def send_verification_email(
        self, 
        email: EmailStr, 
        username: str, 
        verification_token: str
    ) -> bool:
        """
        Send email verification link
        """
        verification_link = f"https://yourapp.com/verify-email?token={verification_token}"
        
        return await self.send_email(
            recipient=email,
            username=username,
            subject="Verify Your Email",
            template_name="verification_email_template.html",
            template_body={
                "username": username,
                "verification_link": verification_link
            }
        )

# Singleton instance
email_service = EmailService()
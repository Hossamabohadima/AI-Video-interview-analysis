import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template


class EmailService:
    """Service for sending emails using SMTP."""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@interviewme.com")
        self.from_name = os.getenv("FROM_NAME", "InterviewMe")
        
        if not self.smtp_username or not self.smtp_password:
            print("Warning: SMTP credentials not configured. Emails will not be sent.")
    
    def _create_message(self, to_email: str, subject: str, html_body: str, text_body: str = None) -> MIMEMultipart:
        """Create a MIME message."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to_email
        
        if text_body:
            msg.attach(MIMEText(text_body, "plain", "utf-8"))
        
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        return msg
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str = None) -> bool:
        """Send an email via SMTP."""
        if not self.smtp_username or not self.smtp_password:
            print(f"[DEV MODE] Email would be sent to: {to_email}")
            print(f"Subject: {subject}")
            print(f"Body preview: {html_body[:200]}...")
            return True
        
        try:
            msg = self._create_message(to_email, subject, html_body, text_body)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False


# Singleton instance
_email_service = None

def get_email_service() -> EmailService:
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
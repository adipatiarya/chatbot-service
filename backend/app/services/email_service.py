import emails
from app.utils import logger
from app.core.config import settings

class EmailService:
    def __init__(self, email_to:str, subject:str = '', html_content:str=''):
        self.email_to = email_to
        self.subject = subject
        self.html_content = html_content
        
    def send(self) -> None:
      assert settings.emails_enabled, "no provided configuration for email variables"
      message = emails.Message(subject=self.subject,html=self.html_content,mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL))
      smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
      
      if settings.SMTP_TLS:
         smtp_options["tls"] = True
      elif settings.SMTP_SSL:
         smtp_options["ssl"] = True
      if settings.SMTP_USER:
         smtp_options["user"] = settings.SMTP_USER
      if settings.SMTP_PASSWORD:
         smtp_options["password"] = settings.SMTP_PASSWORD
      
      response = message.send(to=self.email_to, smtp=smtp_options)
      logger.info(f"send email result {response}")

import random
import smtplib
from email.message import EmailMessage

from basicvids_auth.settings import settings


def generate_email_code() -> str:
    return f"{random.SystemRandom().randint(0, 999999):06d}"


def send_confirmation_email(email: str, code: str) -> None:
    subject = "BasicVids email confirmation"
    body = f"Your BasicVids confirmation code is: {code}"

    if settings.DEBUG or not settings.SMTP_HOST:
        print(f"[BasicVids email] To: {email}")
        print(f"[BasicVids email] Subject: {subject}")
        print(f"[BasicVids email] {body}")
        return

    message = EmailMessage()
    message["From"] = settings.EMAIL_FROM
    message["To"] = email
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.starttls()
        if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        smtp.send_message(message)

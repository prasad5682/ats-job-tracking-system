from celery import shared_task
from app.core.email import send_email

@shared_task
def send_email_task(to_email, subject, body):
    send_email(to_email, subject, body)

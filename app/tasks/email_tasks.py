from celery import shared_task
from app.core.email import send_email  # actual email sending function


@shared_task
def send_stage_change_email(to_email: str, job_title: str, new_stage: str):
    subject = f"Application Update: {job_title}"
    message = f"Your application stage has changed to: {new_stage}"
    send_email(to_email, subject, message)


@shared_task
def notify_recruiter_new_application(recruiter_email: str, job_title: str, candidate_email: str):
    subject = f"New Application Received for {job_title}"
    message = f"Candidate {candidate_email} applied for the job: {job_title}"
    send_email(recruiter_email, subject, message)

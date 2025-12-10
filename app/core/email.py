from celery_app import celery_app

# Celery Task
@celery_app.task
def send_email_task(to_email: str, subject: str, body: str):
    print("\n====== EMAIL SENT (Celery Worker) ======")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    print("========================================\n")


# FastAPI will call THIS function
def send_email(to_email: str, subject: str, body: str):
    send_email_task.delay(to_email, subject, body)

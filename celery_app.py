from celery import Celery

celery = Celery(
    "worker",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0"
)

# Auto discover tasks from app/tasks
celery.autodiscover_tasks(["app.tasks"])

from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0"
)

# Tell Celery where tasks live
celery_app.autodiscover_tasks([
    "app.tasks"
])

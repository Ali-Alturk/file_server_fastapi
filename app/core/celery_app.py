from celery import Celery
from app.config import settings

celery_app = Celery(
    "worker",
    broker=settings.RABBITMQ_URL,  # Ensure this points to your RabbitMQ broker
    backend=settings.CELERY_RESULT_BACKEND,  # Add a valid result backend
    include=["app.tasks.file_processing"]
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,  # Task results expire after 1 hour
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    broker_connection_retry_on_startup=True,
)
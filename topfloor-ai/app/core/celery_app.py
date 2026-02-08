"""
Celery Application Configuration
"""

from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "topfloor_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.background_worker"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,  # Process one task at a time per worker
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks
    task_acks_late=True,  # Acknowledge task after completion
    task_reject_on_worker_lost=True,  # Reject task if worker dies
    result_expires=86400,  # Results expire after 24 hours
    broker_connection_timeout=2,
    broker_connection_retry=False,
    broker_connection_retry_on_startup=False,
    broker_transport_options={
        "socket_timeout": 2,
        "socket_connect_timeout": 2
    },
)

# Task routes - route tasks to specific queues based on agent type
celery_app.conf.task_routes = {
    "app.workers.background_worker.process_task": {
        "queue": "default"
    },
}

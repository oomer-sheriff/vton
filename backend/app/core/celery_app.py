from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.worker.tasks', 'app.worker.vton_tasks']
)

celery_app.conf.task_routes = {
    "app.worker.tasks.remove_background_task": "gpu-worker",
    "app.worker.tasks.extract_metadata_task": "cpu-worker",
    "app.worker.tasks.virtual_tryon_task": "gpu-worker",
}

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_queues={
        "gpu-worker": {"exchange": "gpu-worker", "routing_key": "gpu-worker"},
        "cpu-worker": {"exchange": "cpu-worker", "routing_key": "cpu-worker"},
    },
    # Config for Long-Running Tasks (VTON ~15 mins)
    broker_heartbeat=0,              # Disable heartbeat to prevent timeouts during blocking inference
    broker_connection_timeout=3600,  # Allow long connection survival
    worker_prefetch_multiplier=1,    # One task at a time (don't hoard)
    task_acks_late=True,             # Ack only after task is done
    task_track_started=True,         # Track 'STARTED' state
    task_reject_on_worker_lost=True  # Re-queue if worker hard crashes
)

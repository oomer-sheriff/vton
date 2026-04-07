from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.worker.tasks', 'app.worker.vton_tasks', 'app.worker.transformer_tasks']
)

celery_app.conf.task_routes = {
    "app.worker.tasks.remove_background_task":                  {"queue": "gpu-inpainting"},
    "app.worker.tasks.extract_metadata_task":                   {"queue": "cpu-worker"},
    "app.worker.vton_tasks.virtual_tryon_task":                 {"queue": "gpu-inpainting"},
    "app.worker.transformer_tasks.transformer_tryon_task":      {"queue": "gpu-transformer"},
}

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_queues={
        # Inpainting mode: SD 1.5 + DensePose + IP-Adapter (GPU required in worker)
        "gpu-inpainting": {"exchange": "gpu-inpainting", "routing_key": "gpu-inpainting"},
        # Transformer mode: Flux 2 via ComfyUI (worker has no GPU; ComfyUI container does)
        "gpu-transformer": {"exchange": "gpu-transformer", "routing_key": "gpu-transformer"},
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

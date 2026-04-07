from celery import shared_task
from app.db.session import SessionLocal
from app.models.garment import Garment
from uuid import UUID
import shutil
import os


@shared_task(name="app.worker.transformer_tasks.transformer_tryon_task")
def transformer_tryon_task(person_image_path: str, garment_id: str, output_path: str):
    """
    Performs Virtual Try-On using the Flux 2 / ComfyUI transformer pipeline.
    1. Fetches garment processed_image_path from DB.
    2. Dispatches job to ComfyUI service via HTTP.
    3. Moves result to output_path.
    """
    try:
        db = SessionLocal()
        garment = db.query(Garment).filter(Garment.id == UUID(garment_id)).first()
        db.close()

        if not garment or not garment.processed_image_path:
            return {"status": "failed", "error": "Garment not found or not processed"}

        garment_path = garment.processed_image_path.replace("\\", "/")

        # Lazy import — only loads ComfyUI client + opens workflow_api.json when task runs
        # (prevents issues in worker-inpainting which has no gguf/peft installed)
        from app.core.comfyui_pipeline import comfyui_pipeline

        result_path = comfyui_pipeline.run(person_image_path, garment_path)

        if result_path != output_path and os.path.exists(result_path):
            shutil.move(result_path, output_path)

        return {"status": "completed", "result_path": output_path}

    except Exception as e:
        return {"status": "failed", "error": str(e)}

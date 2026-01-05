from celery import shared_task
from app.core.vton_pipeline import vton_pipeline
from app.db.session import SessionLocal
from app.models.garment import Garment
from uuid import UUID
import shutil
import os

@shared_task(name="app.worker.tasks.virtual_tryon_task")
def virtual_tryon_task(person_image_path: str, garment_id: str, output_path: str):
    """
    Performs Virtual Try-On.
    1. Fetches garment processed path from DB.
    2. Runs VTON pipeline.
    3. Saves result.
    """
    try:
        db = SessionLocal()
        garment = db.query(Garment).filter(Garment.id == UUID(garment_id)).first()
        db.close()

        if not garment or not garment.processed_image_path:
            return {"status": "failed", "error": "Garment not found or not processed"}

        garment_path = garment.processed_image_path.replace("\\", "/")
        
        # Run Pipeline
        # In a real scenario, this returns a PIL Image or saves to path.
        # Our current skeleton returns the path it saved to.
        result_path = vton_pipeline.run(person_image_path, garment_path)
        
        # Ensure result is moved/saved to final output_path if pipeline didn't do it
        if result_path != output_path and os.path.exists(result_path):
             shutil.move(result_path, output_path)

        return {"status": "completed", "result_path": output_path}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

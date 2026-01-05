from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import shutil
import os
import uuid
from app.worker.vton_tasks import virtual_tryon_task
from app.core.celery_app import celery_app

router = APIRouter()

UPLOAD_DIR = "media/raw"
RESULTS_DIR = "media/results"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

@router.post("/")
async def tryon(
    person_image: UploadFile = File(...),
    garment_id: str = Form(...)
):
    """
    Trigger a Virtual Try-On task.
    """
    if person_image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
         raise HTTPException(status_code=400, detail="Invalid image type")

    # Save Person Image
    task_uuid = uuid.uuid4()
    task_id = str(task_uuid)
    ext = person_image.filename.split(".")[-1]
    
    person_filename = f"{task_id}_person.{ext}"
    person_path = os.path.join(UPLOAD_DIR, person_filename)
    
    output_filename = f"{task_id}_tryon.png"
    output_path = os.path.join(RESULTS_DIR, output_filename)

    try:
        with open(person_path, "wb") as buffer:
            shutil.copyfileobj(person_image.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

    # Trigger Task
    task = virtual_tryon_task.delay(person_path, garment_id, output_path)

    return {
        "message": "Try-On process started",
        "task_id": task.id,
        "result_path_placeholder": output_path
    }

@router.get("/status/{task_id}")
def get_tryon_status(task_id: str):
    task_result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result
    }

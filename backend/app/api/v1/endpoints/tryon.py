from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from enum import Enum
import shutil
import os
import uuid
from app.worker.vton_tasks import virtual_tryon_task
from app.worker.transformer_tasks import transformer_tryon_task
from app.core.celery_app import celery_app

router = APIRouter()

UPLOAD_DIR = "media/raw"
RESULTS_DIR = "media/results"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


class TryOnMode(str, Enum):
    inpainting = "inpainting"
    transformer = "transformer"


@router.post("/")
async def tryon(
    person_image: UploadFile = File(...),
    garment_id: str = Form(...),
    mode: TryOnMode = Form(TryOnMode.inpainting),
):
    """
    Trigger a Virtual Try-On task.

    - **mode=inpainting** (default): SD 1.5 + DensePose + IP-Adapter pipeline.
      Runs inside the `worker-inpainting` container which has a GPU.
    - **mode=transformer**: Flux 2 Klein 4B via ComfyUI.
      Dispatched to `worker-transformer`, which calls the `comfyui` container.
    """
    if person_image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid image type")

    # Save Person Image
    task_uuid = uuid.uuid4()
    task_id = str(task_uuid)
    ext = person_image.filename.split(".")[-1]

    person_filename = f"{task_id}_person.{ext}"
    person_path = os.path.join(UPLOAD_DIR, person_filename).replace("\\", "/")

    output_filename = f"{task_id}_tryon.png"
    output_path = os.path.join(RESULTS_DIR, output_filename).replace("\\", "/")

    try:
        with open(person_path, "wb") as buffer:
            shutil.copyfileobj(person_image.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

    # Dispatch to the appropriate queue / worker
    if mode == TryOnMode.transformer:
        task = transformer_tryon_task.apply_async(
            args=[person_path, garment_id, output_path],
            queue="gpu-transformer",
        )
    else:
        task = virtual_tryon_task.apply_async(
            args=[person_path, garment_id, output_path],
            queue="gpu-inpainting",
        )

    return {
        "message": "Try-On process started",
        "task_id": task.id,
        "mode": mode,
        "result_path_placeholder": output_path,
    }


@router.get("/status/{task_id}")
def get_tryon_status(task_id: str):
    task_result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }

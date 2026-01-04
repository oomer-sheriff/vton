from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import uuid
from app.worker.tasks import remove_background_task, extract_metadata_task

router = APIRouter()

UPLOAD_DIR = "media/raw"
PROCESSED_DIR = "media/processed"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

@router.post("/upload")
async def upload_garment(file: UploadFile = File(...)):
    """
    Upload a raw garment image.
    Triggers background removal and metadata extraction tasks.
    Returns task IDs.
    """
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, WEBP allowed.")

    # Generate unique ID
    file_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1]
    
    # Paths
    raw_filename = f"{file_id}.{extension}"
    raw_path = os.path.join(UPLOAD_DIR, raw_filename)
    
    processed_filename = f"{file_id}_clean.png"
    processed_path = os.path.join(PROCESSED_DIR, processed_filename)

    # Save Uploaded File
    try:
        with open(raw_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

    # Trigger Celery Tasks
    # 1. Background Removal
    rembg_task = remove_background_task.delay(raw_path, processed_path)
    
    # 2. Metadata Extraction
    metadata_task = extract_metadata_task.delay(raw_path)

    return {
        "message": "File uploaded and processing started",
        "file_id": file_id,
        "tasks": {
            "background_removal": rembg_task.id,
            "metadata_extraction": metadata_task.id
        },
        "raw_path": raw_path
    }

@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    from app.core.celery_app import celery_app
    task_result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result
    }

@router.get("/")
def get_ingestion_status():
    return {"status": "Ingestion service ready"}

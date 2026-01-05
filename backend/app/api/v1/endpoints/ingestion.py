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

# Additional imports
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.garment import Garment

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload")
async def upload_garment(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a raw garment image.
    Creates a Garment record in DB.
    Triggers background removal and metadata extraction tasks.
    Returns task IDs and garment ID.
    """
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, WEBP allowed.")

    # Generate unique ID (we use uuid for file safety, and let DB generate its own if we didn't specify, 
    # but here we reuse the file_id for DB id as well for consistency)
    file_uuid = uuid.uuid4()
    file_id = str(file_uuid)
    extension = file.filename.split(".")[-1]
    
    # Paths
    raw_filename = f"{file_id}.{extension}"
    raw_path = os.path.join(UPLOAD_DIR, raw_filename).replace("\\", "/")
    
    processed_filename = f"{file_id}_clean.png"
    processed_path = os.path.join(PROCESSED_DIR, processed_filename).replace("\\", "/")

    # Save Uploaded File
    try:
        with open(raw_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

    # Create DB Record
    garment = Garment(
        id=file_uuid,
        filename=file.filename,
        raw_image_path=raw_path
    )
    db.add(garment)
    db.commit()
    db.refresh(garment)

    # Trigger Celery Tasks
    # 1. Background Removal
    rembg_task = remove_background_task.delay(raw_path, processed_path, file_id)
    
    # 2. Metadata Extraction
    metadata_task = extract_metadata_task.delay(raw_path, file_id)

    return {
        "message": "File uploaded and processing started",
        "file_id": file_id,
        "garment_id": str(garment.id),
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

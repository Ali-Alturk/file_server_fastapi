import logging
import hashlib
import os
import time
import random
import string
from typing import Any, List
from celery.result import AsyncResult
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, logger, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.config import settings
from app.crud import file as file_crud
from app.models.user import User
from app.schemas.file import FileUpload, FileUploadResponse, TaskStatus
from app.tasks.file_processing import process_uploaded_file, process_multiple_files

logger = logging.getLogger(__name__)

router = APIRouter()


def generate_file_hash(filename: str) -> str:
    """Generate a unique hash for the file"""
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    hash_string = f"{time.time()}{random_string}{filename}"
    return hashlib.sha256(hash_string.encode()).hexdigest()


async def save_upload_file(file: UploadFile, file_hash: str) -> str:
    """Save uploaded file to disk and return the file path"""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file_hash)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds the limit of {settings.MAX_UPLOAD_SIZE} bytes",
            )
        buffer.write(content)
    
    return file_path


@router.post("/files/upload", response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload a single file and process it in the background.
    """
    try:
        # Generate file hash
        file_hash = generate_file_hash(file.filename)

        # Save the uploaded file
        file_path = await save_upload_file(file, file_hash)

        # Create file record in the database
        file_data = {
            "file_hash": file_hash,
            "original_filename": file.filename,
            "file_path": file_path,
            "user_id": current_user.id,
            "status": "pending"
        }
        db_file = file_crud.create(db, file_data)

        # Dispatch the task to process the file
        task = process_uploaded_file.delay(file_hash)

        # Save task info in the database
        task_data = {
            "task_id": task.id,
            "status": "pending"
        }
        file_crud.create_task_status(db, task_data)
        db.commit()

        return {
            "task_id": task.id,
            "file_hash": file_hash,
            "status": "processing"
        }
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


@router.post("/files/upload-multiple", response_model=List[FileUploadResponse])
async def upload_multiple_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    # ... existing validation code ...

    file_hashes = []
    response = []
    for file in files:
        file_hash = generate_file_hash(file.filename)
        file_hashes.append(file_hash)
        file_path = await save_upload_file(file, file_hash)
        
        # Create file record in the database
        file_data = {
            "file_hash": file_hash,
            "original_filename": file.filename,
            "file_path": file_path,
            "user_id": current_user.id,
            "status": "pending"
        }
        db_file = file_crud.create(db, file_data)
    
    # Process files in background
    task = process_multiple_files.delay(file_hashes)
    
    # Prepare response with initial processing status
    response = [{
        "file_hash": file_hash,
        "task_id": task.id,
        "status": "processing"
    } for file_hash in file_hashes]
    
    return response


@router.get("/files/task-status/{task_id}", response_model=TaskStatus)
def check_task_status(
    task_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Check the status of a file processing task with enhanced debugging.
    """
    logger.info(f"Checking status for task_id: {task_id}")
    
    # Retrieve task status from database
    task_status = file_crud.get_task_status(db, task_id)
    
    if task_status:
        logger.info(f"Task status found in database: {task_status.__dict__}")
        return task_status
    
    # Check Celery task status as a fallback
    try:
        celery_task = AsyncResult(task_id)
        logger.info(f"Celery task status: {celery_task.status}")
        
        if celery_task.status and celery_task.status.lower() in ["pending", "started", "success", "failure"]:
            task_data = {
                "task_id": task_id,
                "status": celery_task.status.lower()
            }
            task_status = file_crud.create_task_status(db, task_data)
            db.commit()
            return task_status
        else:
            logger.warning(f"Task {task_id} not found in Celery.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found in both database and Celery"
            )
    except Exception as e:
        logger.error(f"Error retrieving Celery task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving Celery task status: {str(e)}"
        )


@router.get("/files", response_model=List[FileUpload])
def get_user_files(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all files uploaded by the current user.
    """
    return file_crud.get_user_files(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
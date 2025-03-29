import logging
from celery.result import AsyncResult
from typing import List, Dict, Any
from celery import shared_task
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import file as file_crud

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_uploaded_file(self, file_hash: str) -> dict:
    logger.info(f"Task started for file_hash: {file_hash}")
    db = SessionLocal()
    try:
        # Get the file record
        file_record = file_crud.get(db, file_hash)
        if not file_record:
            logger.error(f"File with hash {file_hash} not found")
            file_crud.update_task_status(db, self.request.id, "failed")
            db.commit()
            return {"status": "error", "file_hash": file_hash, "error": "File not found"}

        # Update file status to "processing"
        file_crud.update(
            db,
            db_obj=file_record,
            obj_in={"status": "processing"}
        )
        db.commit()

        # Simulate file processing
        logger.info(f"Processing file with hash: {file_hash}")
        # Add your file processing logic here...

        # Update file status to "processed"
        file_crud.update(
            db,
            db_obj=file_record,
            obj_in={"status": "processed"}
        )
        db.commit()

        # Update task status to "completed"
        file_crud.update_task_status(db, self.request.id, "completed")
        db.commit()

        logger.info(f"Task completed for file_hash: {file_hash}")
        return {"status": "success", "file_hash": file_hash}
    except Exception as e:
        logger.error(f"Error processing file {file_hash}: {str(e)}")
        file_crud.update_task_status(db, self.request.id, "failed")
        db.commit()
        return {"status": "error", "file_hash": file_hash, "error": str(e)}
    finally:
        db.close()

@shared_task(bind=True)
def process_multiple_files(self, file_hashes: List[str]) -> List[dict]:
    """
    Process multiple uploaded files.

    This is a Celery task that runs in the background.
    """
    logger.info(f"Starting to process multiple files: {file_hashes}")
    db = SessionLocal()
    results = []

    try:
        # Save the parent task in the database
        logger.info(f"Saving parent task info for task_id: {self.request.id}")
        file_crud.create_task_status(db, {"task_id": self.request.id, "status": "pending"})
        db.commit()

        # Dispatch individual tasks for each file
        tasks = []
        for file_hash in file_hashes:
            try:
                # Get the file record
                file_record = file_crud.get(db, file_hash)
                if not file_record:
                    logger.error(f"File with hash {file_hash} not found")
                    results.append({
                        "status": "error",
                        "file_hash": file_hash,
                        "error": "File not found"
                    })
                    continue

                # Update file status to "processing"
                logger.info(f"Updating file status to 'processing' for file_hash: {file_hash}")
                file_crud.update(
                    db,
                    db_obj=file_record,
                    obj_in={"status": "processing"}
                )
                db.commit()

                # Dispatch the task for this file
                logger.info(f"Dispatching task for file_hash: {file_hash}")
                task = process_uploaded_file.delay(file_hash)
                tasks.append((task, file_hash))

                results.append({
                    "file_hash": file_hash,
                    "task_id": task.id,
                    "status": "processing"
                })
            except Exception as e:
                logger.error(f"Error in processing file {file_hash}: {str(e)}")
                results.append({
                    "status": "error",
                    "file_hash": file_hash,
                    "error": str(e)
                })

        # Wait for all tasks to complete and update statuses
        for task, file_hash in tasks:
            try:
                logger.info(f"Checking status for task_id: {task.id}")
                task_result = AsyncResult(task.id)

                # Update file statuses based on the task result
                if task_result.state == "SUCCESS":
                    logger.info(f"Task {task.id} completed successfully for file_hash: {file_hash}")
                    file_record = file_crud.get(db, file_hash)
                    if file_record:
                        file_crud.update(
                            db,
                            db_obj=file_record,
                            obj_in={"status": "processed"}
                        )
                    db.commit()
                elif task_result.state == "FAILURE":
                    logger.info(f"Task {task.id} failed for file_hash: {file_hash}")
                    file_record = file_crud.get(db, file_hash)
                    if file_record:
                        file_crud.update(
                            db,
                            db_obj=file_record,
                            obj_in={"status": "failed"}
                        )
                    db.commit()
                else:
                    logger.info(f"Task {task.id} is still in state: {task_result.state}")
            except Exception as e:
                logger.error(f"Error checking status for task {task.id}: {str(e)}")
                file_record = file_crud.get(db, file_hash)
                if file_record:
                    file_crud.update(
                        db,
                        db_obj=file_record,
                        obj_in={"status": "failed"}
                    )
                db.commit()

        # Update the status of the parent task (process_multiple_files)
        logger.info(f"Updating parent task status to 'completed' for task_id: {self.request.id}")
        file_crud.update_task_status(db, self.request.id, "completed")
        db.commit()

    except Exception as e:
        logger.error(f"Error in processing multiple files: {str(e)}")
        logger.info(f"Updating parent task status to 'failed' for task_id: {self.request.id}")
        file_crud.update_task_status(db, self.request.id, "failed")
        db.rollback()
    finally:
        db.close()

    return results
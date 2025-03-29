from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.file import FileUpload, TaskStatus
from app.schemas.file import FileUploadCreate, FileUploadUpdate, TaskStatusCreate


def get(db: Session, file_hash: str) -> Optional[FileUpload]:
    return db.query(FileUpload).filter(FileUpload.file_hash == file_hash).first()

def create(db: Session, obj_in: Dict[str, Any]) -> FileUpload:
    db_obj = FileUpload(**obj_in)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, db_obj, obj_in: dict) -> None:
    for key, value in obj_in.items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)

def get_user_files(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[FileUpload]:
    return db.query(FileUpload).filter(FileUpload.user_id == user_id).offset(skip).limit(limit).all()

def create_task_status(db: Session, task_data: dict) -> TaskStatus:
    task_status = TaskStatus(**task_data)
    db.add(task_status)
    return task_status

def get_task_status(db: Session, task_id: str) -> Optional[TaskStatus]:
    return db.query(TaskStatus).filter(TaskStatus.task_id == task_id).first()

def update_task_status(db: Session, task_id: str, status: str) -> None:
    task_status = db.query(TaskStatus).filter(TaskStatus.task_id == task_id).first()
    if task_status:
        task_status.status = status
        db.commit()
        db.refresh(task_status)
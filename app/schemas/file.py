from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class FileUploadBase(BaseModel):
    original_filename: str


class FileUploadCreate(FileUploadBase):
    pass


class FileUploadUpdate(BaseModel):
    status: Optional[str] = None
    is_deleted: Optional[bool] = None


class FileUploadInDB(FileUploadBase):
    file_hash: str
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        orm_mode = True


class FileUpload(FileUploadBase):
    file_hash: str
    status: str
    created_at: datetime
    is_deleted: bool

    class Config:
        orm_mode = True


class FileUploadResponse(BaseModel):
    task_id: str
    file_hash: str
    status: str


class TaskStatusBase(BaseModel):
    task_id: str
    status: str


class TaskStatusCreate(TaskStatusBase):
    pass


class TaskStatusInDB(TaskStatusBase):
    id: int
    created_at: datetime
    updated_at: datetime
    result: Optional[dict] = None

    class Config:
        orm_mode = True


class TaskStatus(TaskStatusBase):
    result: Optional[dict] = None

    class Config:
        orm_mode = True
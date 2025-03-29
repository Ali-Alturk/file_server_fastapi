from pydantic_settings import BaseSettings
from typing import ClassVar, List
import secrets
from functools import lru_cache



class Settings(BaseSettings):
    # Base settings
    PROJECT_NAME: str = "File Server API"
    PROJECT_DESCRIPTION: str = "An API for file uploads and processing"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Database
    DATABASE_URL: str = "mysql://root:1234@localhost:3306/fastapi_fileserver_db"

    # File upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 52428800  # 50 MB
    CHUNK_SIZE: int = 2621440  # 2.5 MB

    # Define all fields with type annotations
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672//"
    CELERY_RESULT_BACKEND: str = "rpc://"

    # Example of other settings
    APP_NAME: str = "File Server"
    DEBUG: bool = True

    # If you have constants that are not meant to be fields, use ClassVar
    SOME_CONSTANT: ClassVar[str] = "This is a constant"


    class Config:
        env_file = ".env"
        case_sensitive = True
        

@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
import uvicorn
from app.database import init_db

if __name__ == "__main__":
    # Initialize database tables if they don't exist
    init_db()
    # Run the FastAPI application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
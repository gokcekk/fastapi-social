# app/main.py

from fastapi import FastAPI

from app.db.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router

# Create the main FastAPI application object
# This is what Uvicorn runs: `uvicorn app.main:app --reload`
app = FastAPI(
    title="Social Network API",  # Title shown in the Swagger UI
    version="0.1.0",             # API version, useful for documentation
)

# Create all database tables based on the SQLAlchemy models
# This is suitable for local development or very early stages
# In a real project you normally use migrations (for example Alembic)
Base.metadata.create_all(bind=engine)

# Attach the routers to the main application
# `prefix="/api/v1"` means all endpoints from these routers
# will start with `/api/v1/...`
app.include_router(auth_router, prefix="/api/v1")   # endpoints for authentication and tokens
app.include_router(users_router, prefix="/api/v1")  # endpoints for user CRUD operations


@app.get("/")
def read_root():
    """
    Health check endpoint.
    Useful for seeing if the API is running.
    Returns a simple JSON message.
    """
    return {"message": "Social Network API is running"}

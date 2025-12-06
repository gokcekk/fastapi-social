# app/main.py

from fastapi import FastAPI

from app.db.database import Base, engine
from app import models  # make sure all models are imported
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.posts import router as posts_router
from app.routers.friend_request import router as friend_request_router
from app.routers.groups import router as groups_router


# Main FastAPI application
app = FastAPI(
    title="Social Network API",
    version="0.1.0",
)


# Create all database tables based on the SQLAlchemy models
# This is suitable for local development or very early stages
# In a real project you normally use migrations (for example Alembic)
Base.metadata.create_all(bind=engine)


# Include routers
app.include_router(auth_router)      # authentication and tokens
app.include_router(users_router)     # user profile endpoints
app.include_router(posts_router)     # posts on user walls
app.include_router(friend_request_router)  
app.include_router(groups_router)


@app.get("/")
def read_root():
    """
    Simple health check endpoint.
    """
    return {"message": "Social Network API is running"}

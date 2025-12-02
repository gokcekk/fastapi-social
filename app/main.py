from fastapi import FastAPI
from .routers import posts
from .database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Simple Social Network API")

# Include router
app.include_router(posts.router)

<<<<<<< Updated upstream
=======
@app.get("/")
def read_root():
    """
    Health check endpoint.
    Useful for seeing if the API is running.
    Returns a simple JSON message.
    """
    return {"message": "Social Network API is running"}


from fastapi import FastAPI
from app.routers.friend_requests import router as friend_request_router

app = FastAPI(title="Social Network - Friend Request System")

app.include_router(friend_request_router)

<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

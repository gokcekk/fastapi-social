from fastapi import FastAPI
from .routers import posts
from .database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Simple Social Network API")

# Include router
app.include_router(posts.router)


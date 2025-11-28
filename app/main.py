from fastapi import FastAPI
from .routers import posts
from .database import engine, Base
from .routers import wall 

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Simple Social Network API")

# Include router
app.include_router(posts.router)
app.include_router(wall.router)
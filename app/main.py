from fastapi import FastAPI
#from .routers import posts
from .routers import users
from .db.database import engine, Base
from .models import user as user_model

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Simple Social Network API")

# Include router
#app.include_router(posts.router)
app.include_router(users.router)



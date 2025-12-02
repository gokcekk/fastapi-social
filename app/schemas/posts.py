from pydantic import BaseModel
from datetime import datetime

class PostBase(BaseModel):
    user: str
    content: str

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class GroupBase(BaseModel):
    name: str
    description: Optional[str]  = None

class GroupCreate(GroupBase):  
    pass  


class GroupOut(GroupBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class GroupPostBase(BaseModel):
    content: str


class GroupPostCreate(GroupPostBase):
    pass


class GroupPostOut(GroupPostBase):
    id: int
    group_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

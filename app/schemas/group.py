# app/schemas/group.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GroupBase(BaseModel):

    name: str
    description: Optional[str] = None

class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class GroupRead(GroupBase):
    id:int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class GroupMemberRead(BaseModel):
    user_id: int
    username: str
    is_admin: bool
    joined_at: datetime

    class Config:
        from_attributes = True

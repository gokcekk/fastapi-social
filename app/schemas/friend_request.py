# app/schemas/friend_request.py

from pydantic import BaseModel
from enum import Enum


class RequestStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    denied = "denied"


class FriendRequestCreate(BaseModel):
    to_user_id: int


class FriendRequestUpdate(BaseModel):
    request_id: int
    action: RequestStatus

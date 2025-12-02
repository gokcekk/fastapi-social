from pydantic import BaseModel


class UserCreate(BaseModel):
    user_id: int
    name: str


class FriendRequestCreate(BaseModel):
    from_id: int
    to_id: int


class FriendRequestResponse(BaseModel):
    request_id: int
    action: str  # approve or deny


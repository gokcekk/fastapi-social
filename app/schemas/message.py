from datetime import datetime
from pydantic import BaseModel


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    """
    It is used when sending messages within an existing conversation.
    Just the `content` is sufficient; the `chat_id` comes from the path.
    """
    pass


class DirectMessageCreate(MessageBase):
    """
    To start a new chat or use an existing chat based on a user (receiver_id).
    """
    receiver_id: int


class MessageRead(BaseModel):
    id: int
    sender_id: int
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True

from datetime import datetime
from pydantic import BaseModel


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    """
    Used to send a message in an existing conversation.
    chat_id is taken from the URL path.
    """
    pass


class DirectMessageCreate(MessageBase):
    """
    Used to start or continue a chat with a user.
    receiver_id is the target user.
    """
    receiver_id: int


class MessageRead(BaseModel):
    id: int
    sender_id: int
    content: str
    timestamp: datetime

    class Config:
        orm_mode = True

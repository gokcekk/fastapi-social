from datetime import datetime
from pydantic import BaseModel


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    """
    Var olan bir conversation içinde mesaj atarken kullanılır.
    Sadece content yeterli, chat_id path'ten geliyor.
    """
    pass


class DirectMessageCreate(MessageBase):
    """
    Bir kullanıcıya (receiver_id) göre yeni sohbet başlatmak
    veya var olan sohbeti kullanmak için.
    """
    receiver_id: int


class MessageRead(BaseModel):
    id: int
    sender_id: int
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True

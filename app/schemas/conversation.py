from pydantic import BaseModel


class ConversationRead(BaseModel):
    id: int
    user1_id: int
    user2_id: int

    class Config:
        from_attributes = True


class ConversationStart(BaseModel):
    receiver_id: int

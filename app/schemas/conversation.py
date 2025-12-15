from pydantic import BaseModel


class ConversationRead(BaseModel):
    id: int

    class Config:
        from_attributes = True

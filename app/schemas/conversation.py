from pydantic import BaseModel


class ConversationRead(BaseModel):
    id: int

    class Config:
        orm_mode = True

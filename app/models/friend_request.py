# app/models/friend_request.py


from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class RequestStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    denied = "denied"


class FriendRequest(Base):
    __tablename__ = "friend_request"

    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    to_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    status = Column(Enum(RequestStatus), default=RequestStatus.pending)

    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])

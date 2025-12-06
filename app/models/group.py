# app/models/group.py

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)

    # Name of the group, shown in the UI
    name = Column(String(100), nullable=False)

    # Optional description of the group
    description = Column(Text, nullable=True)

    # When the group was created
    created_at = Column(DateTime, default=datetime.utcnow)

    # The user who created the group
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship to the User model
    owner = relationship("User", back_populates="groups_owned")

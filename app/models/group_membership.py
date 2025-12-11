# app/models/group_membership.py

from datetime import datetime

from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.timestamp_mixin import TimestampMixin

class GroupMembership(TimestampMixin, Base):
    __tablename__ = "group_memberships"

    id = Column(Integer, primary_key=True, index=True)

    # Which group this membership belongs to
    group_id = Column(
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Which user is a member of this group
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Is this user an admin in this group?
    is_admin = Column(Boolean, default=False)

    # Relationships
    group = relationship("Group", back_populates="memberships")
    user = relationship("User", back_populates="group_memberships")

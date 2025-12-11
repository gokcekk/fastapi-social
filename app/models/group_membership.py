# app/models/group_membership.py

from datetime import datetime

from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.database import Base

class GroupMembership(Base):
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

    created_at = Column(
        DateTime(timezone=True),     # timezone=True: stores date and time with timezone information.
        server_default=func.now(),   # server_default=func.now(): when the row is first inserted,
                                     # the database automatically sets this field to the current time.
        nullable=False,              # nullable=False: this column cannot be null; every row must have a value.
    )

    # When the row was last updated (updated automatically on change)
    updated_at = Column(
        DateTime(timezone=True),     # Again, stores date and time with timezone information.
        server_default=func.now(),   # Initial value is set to "now" when the row is created.
        onupdate=func.now(),         # onupdate=func.now(): every time the row is updated,
                                     # the database automatically sets this field to the current time.
        nullable=False,              # This column also cannot be null.
    )

    # Relationships
    group = relationship("Group", back_populates="memberships")
    user = relationship("User", back_populates="group_memberships")
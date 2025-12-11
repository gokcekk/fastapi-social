# app/models/group.py

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Table,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

from app.db.database import Base

group_members = Table(
    "group_members",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
)

class Group(Base):

    __tablename__ = "groups"  

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    # created_at = Column(DateTime, default=datetime.utcnow)

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

    # The user who created the group
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship to the User model
    owner = relationship("User", back_populates="groups_owned")

    # All membership rows for this group
    memberships = relationship(
        "GroupMembership",
        back_populates="group",
        cascade="all, delete-orphan",
    )

    members = relationship(
        "User",
        secondary="group_members",
        back_populates="groups",
    )

    posts = relationship(
        "GroupPost",
        back_populates="group",
        cascade="all, delete-orphan",
    )


class GroupPost(Base):
    """
    ST-6.6: group_id, user_id, content
    """

    __tablename__ = "group_posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    group = relationship(
        "Group",
        back_populates="posts",
    )

    author = relationship(
        "User",
        back_populates="group_posts",
    )



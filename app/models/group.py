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
)
from sqlalchemy.orm import relationship

from app.db.database import Base


# Many-to-many: hangi user hangi gruba üye
group_members = Table(
    "group_members",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
)


class Group(Base):
    """
    ST-6.1: Basit Group modeli (name, description)
    """

    __tablename__ = "groups"  

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

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

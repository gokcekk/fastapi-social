# app/models/user.py

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    Table,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.timestamp_mixin import TimestampMixin

# Association table for "friendships" between users.
# This is a self-referential many-to-many:
# - One user can have many friends.
# - Each friend is also a user.
user_friends = Table(
    "user_friends",
    Base.metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "friend_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(TimestampMixin, Base):
    """
    SQLAlchemy ORM model for the "users" table.

    This class represents a user record in the database.
    Each class attribute below is mapped to a column in the "users" table.
    """

    # Name of the table in the database
    __tablename__ = "users"

    # Primary key for the user
    # - Integer
    # - Unique per row
    # - Indexed for faster lookups
    id = Column(Integer, primary_key=True, index=True)

    # Username chosen by the user
    # - Max length: 50 characters
    # - Must be unique
    # - Indexed for fast search by username
    # - Cannot be null (required)
    username = Column(String(50), unique=True, index=True, nullable=False)

    # Email address of the user
    # - Max length: 255 characters
    # - Must be unique
    # - Indexed for fast search by email
    # - Cannot be null (required)
    email = Column(String(255), unique=True, index=True, nullable=False)

    # Hashed password of the user (never store plain-text passwords)
    password_hash = Column(String(255), nullable=False)

    # Flag indicating if the user account is active
    # - Can be used for soft deactivation (instead of deleting the row)
    is_active = Column(Boolean, default=True)


    # Optional profile fields (user can update these later):

    # Display name shown in the UI (full name or nickname)
    display_name = Column(String(100), nullable=True)

    # Short biography or description written by the user
    bio = Column(Text, nullable=True)

    # URL of the avatar image for the user (e.g. profile picture)
    avatar_url = Column(String(255), nullable=True)

    # One-to-many relationship:
    # - One user can have many posts.
    # - "owner" is the attribute on the Post model that points back to User.
    # - cascade="all, delete-orphan" means:
    #     if a User is deleted, their posts are also deleted.
    posts = relationship(
        "Post",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    # Many-to-many relationship for friendships between users.
    # - "friends" is the list of User objects that this user is friends with.
    # - Uses the user_friends association table defined above.
    # - primaryjoin: how this user connects to user_friends.user_id
    # - secondaryjoin: how friends connect to user_friends.friend_id
    # - backref="friends_with" allows reverse access:
    #     other_user.friends_with gives users who have other_user as a friend.
    friends = relationship(
        "User",
        secondary=user_friends,
        primaryjoin=id == user_friends.c.user_id,
        secondaryjoin=id == user_friends.c.friend_id,
        backref="friends_with",
    )


    groups_owned = relationship(
        "Group",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    # All group memberships for this user
    group_memberships = relationship(
        "GroupMembership",
        back_populates="user",
        cascade="all, delete-orphan",
    )
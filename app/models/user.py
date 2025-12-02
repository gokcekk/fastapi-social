# app/models/user.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text

from app.db.database import Base


class User(Base):
    
    # SQLAlchemy ORM model for the users table.

    # This class represents a user record in the database.
    # Each attribute below is mapped to a column in the users table.
    

    # Name of the table in the database
    __tablename__ = "users"

    # Primary key for the user
    # Integer, unique per row, indexed for faster lookups
    id = Column(Integer, primary_key=True, index=True)

    # Username chosen by the user
    # - Limited to 50 characters
    # - Must be unique
    # - Indexed for fast search by username
    # - Cannot be null (required)
    username = Column(String(50), unique=True, index=True, nullable=False)

    # Email address of the user
    # - Limited to 255 characters
    # - Must be unique
    # - Indexed for fast search by email
    # - Cannot be null (required)
    email = Column(String(255), unique=True, index=True, nullable=False)

    # Hashed password of the user
    # We never store the plain password, only the hash
    password_hash = Column(String(255), nullable=False)

    # Flag indicating if the user account is active
    # Used for soft deactivation of users
    is_active = Column(Boolean, default=True)

    # When the user record was created
    # Stored in UTC and set automatically when the record is created
    created_at = Column(DateTime, default=datetime.utcnow)

    # Profile fields
    # These fields are optional and can be updated by the user later

    # Display name shown in the UI, for example full name or nickname
    display_name = Column(String(100), nullable=True)

    # Short biography or description written by the user
    bio = Column(Text, nullable=True)

    # URL of the avatar image for the user
    # For example, a link to a profile picture
    avatar_url = Column(String(255), nullable=True)

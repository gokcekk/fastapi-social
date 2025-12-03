# app/schemas/user.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """
    Shared fields for user related schemas.

    This is not used directly as request or response.
    It is a common base class for other schemas like:
    - UserCreate (request)
    - UserRead (response)

    Fields:
    - username: the unique name chosen by the user
    - email: validated as an email address by Pydantic (EmailStr)
    """
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """
    Schema for creating a new user (REQUEST body).

    Used in:
    - POST /api/v1/auth/register

    Client sends:
    - username
    - email
    - password

    This schema is only for input, not for output.
    """
    password: str


class UserRead(UserBase):
    """
    Schema for reading user data (RESPONSE body).

    Used in:
    - POST /auth/register (response_model=UserRead)
    - GET /api/v1/users/me (response_model=UserRead)
    - PUT /api/v1/users/me (response_model=UserRead)

    It defines what the API returns to the client
    when sending back user information.

    Includes:
    - All public fields that can be shown safely.
    Does NOT include:
    - password_hash (this stays only in the database model)
    """
    id: int
    is_active: bool
    created_at: datetime

    # Profile fields that can be displayed in the UI.
    # They are optional, so they can be null in the database.
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        # This tells Pydantic that it can read data from ORM objects,
        # such as SQLAlchemy models, using attribute access.
        # Example:
        # - You can return a User model from SQLAlchemy
        # - FastAPI will convert it to UserRead automatically.
        from_attributes = True


class UserUpdate(BaseModel):
    """
    Schema for updating profile information (REQUEST body).

    Used in:
    - PUT /api/v1/users/me

    All fields are optional:
    - If a field is provided, it will be updated.
    - If a field is not provided, it will not be changed.
    """
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserLogin(BaseModel):
    """
    Schema for login credentials (REQUEST body).

    Used in:
    - POST /api/v1/auth/login

    Client sends:
    - username
    - password

    The backend checks these credentials and, if they are valid,
    returns an access token (using the Token schema in auth.py).
    """
    username: str
    password: str

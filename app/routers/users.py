#app/routers/users.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session


from app.core.auth import get_current_user
from app.schemas.user import UserRead, UserUpdate
from app.models.user import User
from app.db.database import get_db


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
        "/me", 
        response_model=UserRead,
        status_code=status.HTTP_200_OK,
        )
def read_current_user(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return current_user


@router.put(
        "/me", 
        response_model=UserRead,
        status_code=status.HTTP_201_CREATED)
def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the profile of the currently authenticated user."""

    # Update only fields that are provided
    if user_update.display_name is not None:
        current_user.display_name = user_update.display_name

    if user_update.bio is not None:
        current_user.bio = user_update.bio

    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user
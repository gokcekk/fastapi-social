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
        "/me", response_model=UserRead,
        status_code=status.HTTP_201_CREATED,
        )
def read_current_user(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return current_user


@router.put(
        "/me", response_model=UserRead,
         status_code=status.HTTP_201_CREATED,)
def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the profile of the currently authenticated user."""

    return update_user_profile(
        user_update=user_update,
        db=db,
        current_user=current_user,
    )
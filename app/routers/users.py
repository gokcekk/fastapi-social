# app/routers/users.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.schemas.user import UserRead, UserUpdate
from app.models.user import User
from app.db.database import get_db
from app.services.user import update_user_profile


# All user-related endpoints will be under the /users prefix
router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    """
    Get the profile of the currently authenticated user.

    How it works:
    - get_current_user reads and validates the JWT token.
    - If the token is valid, it loads the User from the database.
    - We simply return that User as a UserRead schema.
    """
    return current_user


@router.put(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the profile of the currently authenticated user.

    Flow:
    - get_current_user gives us the logged-in User (current_user).
    - user_update contains the fields that can be changed (from the request body).
    - We pass everything to the user service (update_user_profile),
      which handles the actual update logic.
    - The updated user is returned as a UserRead schema.
    """
    return update_user_profile(
        user_update=user_update,
        db=db,
        current_user=current_user,
    )

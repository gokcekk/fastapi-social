# app/services/user.py

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserUpdate


def update_user_profile(
    user_update: UserUpdate,
    db: Session,
    current_user: User,
) -> User:
    """
    Update the profile fields of the current user.

    Rules:
    - Only update fields that are actually provided (not None) in UserUpdate.
    - This allows partial updates:
        * If the client sends only "bio", we do not change display_name or avatar_url.
    """

    # Update only fields that are provided (not None) in the request
    if user_update.display_name is not None:
        current_user.display_name = user_update.display_name

    if user_update.bio is not None:
        current_user.bio = user_update.bio

    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url

    # Persist changes to the database
    db.add(current_user)
    db.commit()
    db.refresh(current_user)  # Reload from DB to get the latest state

    return current_user

# app/services/user.py

from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserUpdate



def update_user_profile(
        user_update:UserUpdate,
        db:Session,
        current_user:User,
    ) -> User:

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
# app/services/group.py

from sqlalchemy.orm import Session

from app.models.group import Group
from app.models.user import User
from app.schemas.group import GroupCreate


def create_group(
    db: Session,
    group_in: GroupCreate,
    current_user: User,
) -> Group:

    db_group = Group(
        name=group_in.name,
        description=group_in.description,
        owner_id=current_user.id,
    )

    db.add(db_group)
    db.commit()
    db.refresh(db_group)

    return db_group

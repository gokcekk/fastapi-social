# app/services/group.py

from sqlalchemy.orm import Session

from app.models.group import Group
from app.models.user import User
from app.schemas.group import GroupCreate
from app.models.group_membership import GroupMembership



def create_group(
    db: Session,
    group_in: GroupCreate,
    current_user: User,
) -> Group:
    """
    Create a new group and make the current user an admin member.
    """

    # 1) Create the group
    db_group = Group(
        name=group_in.name,
        description=group_in.description,
        owner_id=current_user.id,
    )

    db.add(db_group)
    db.commit()
    db.refresh(db_group)

        # 2) Create a membership row for the creator as admin
    membership = GroupMembership(
        group_id=db_group.id,
        user_id=current_user.id,
        is_admin=True,
    )

    db.add(membership)
    db.commit()


    return db_group

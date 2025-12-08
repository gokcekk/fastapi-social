# app/services/group.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.group import Group
from app.models.user import User
from app.schemas.group import GroupCreate, GroupUpdate
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


def is_user_admin_in_group(
    db: Session,
    group_id: int,
    current_user: User,
) -> bool:
    """
    Return True if current_user is an admin in the given group, else False.
    """
    membership = (
        db.query(GroupMembership)
        .filter(
            GroupMembership.group_id == group_id,
            GroupMembership.user_id == current_user.id,
        )
        .first()
    )

    if membership is None:
        return False
    if membership.is_admin:
        return True

    return False


def update_group(
    db: Session,
    group_id: int,
    group_in: GroupUpdate,
    current_user: User,
) -> Group:
    """
    Update a group's name/description if the current user is an admin.
    """

    # 1) Check if current_user is admin in this group
    is_admin = is_user_admin_in_group(
        db=db,
        group_id=group_id,
        current_user=current_user,
    )
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not an admin of this group.",
        )

    # 2) Load the group from the database
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if db_group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found.",
        )

    # 3) Update fields only if they are provided
    if group_in.name is not None:
        db_group.name = group_in.name

    if group_in.description is not None:
        db_group.description = group_in.description

    # 4) Save changes and return the updated group
    db.commit()
    db.refresh(db_group)

    return db_group


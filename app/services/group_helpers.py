#app/services/group_helpers.py
from sqlalchemy.orm import Session

from app.models.group import Group
from app.models.user import User
from app.models.group_membership import GroupMembership
from fastapi import HTTPException, status




def get_group_or_404(
        db: Session, 
        group_id: int
        ) -> Group:

    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found.",
    )

    return group

def is_member(db: Session, group_id: int, user_id: int) -> bool:

    return db.query(GroupMembership).filter(
        GroupMembership.group_id == group_id,
        GroupMembership.user_id == user_id,
    ).first() is not None  


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

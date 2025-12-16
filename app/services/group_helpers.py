#app/services/group_helpers.py
from sqlalchemy.orm import Session

from app.models.group import Group
from app.models.user import User
from app.models.group_membership import GroupMembership
from app.core.exaption_messages import Messages
from app.core.exceptions import NotFoundError



def get_group_or_404(
        db: Session, 
        group_id: int
        ) -> Group:

    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise NotFoundError(Messages.GROUP_NOT_FOUND,
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

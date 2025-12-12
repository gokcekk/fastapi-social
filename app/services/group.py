# app/services/group.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from sqlalchemy.exc import IntegrityError

from app.models.group import Group, GroupPost 
from app.models.user import User
from app.schemas.group import GroupMemberRead, GroupUpdate, GroupPostCreate    
from app.models.group_membership import GroupMembership
from app.core.exaption_messages import Messages

# def create_group(
#     db: Session,
#     group_in: GroupCreate,
#     current_user: User,
# ) -> Group:
#     """
#     Create a new group and make the current user an admin member.
#     """

#     # 1) Create the group
#     db_group = Group(
#         name=group_in.name,
#         description=group_in.description,
#         owner_id=current_user.id,
#     )

#     db.add(db_group)
#     db.commit()
#     db.refresh(db_group)

#     # 2) Create a membership row for the creator as admin
#     membership = GroupMembership(
#         group_id=db_group.id,
#         user_id=current_user.id,
#         is_admin=True,
#     )

#     db.add(membership)
#     db.commit()

#     return db_group

def _get_group_or_404(db: Session, group_id: int) -> Group:

    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Messages.GROUP_NOT_FOUND,
        )
    return group

def _is_member(db: Session, group_id: int, user_id: int) -> bool:

    return db.query(GroupMembership).filter(
        GroupMembership.group_id == group_id,
        GroupMembership.user_id == user_id,
    ).first() is not None

def join_group(
        db: Session, 
        group_id: int, 
        current_user: User) -> dict:
    """
    Let the current authenticated user join a group.

    This uses the GroupMembership table:
    - If the group does not exist, raise 404.
    - If the user is already a member, return an idempotent message.
    - Otherwise, create a new membership row and commit.
    """

    # 1) Ensure the group exists (404 if not)
    _get_group_or_404(db, group_id)

    # 2) Check if the user is already a member of this group
    existing = (
        db.query(GroupMembership)
        .filter(
            GroupMembership.group_id == group_id,
            GroupMembership.user_id == current_user.id,
        )
        .first()
    )

    if existing:
        # We keep this idempotent: no error, just a "already member" message
        return {"detail": Messages.ALREADY_MEMBER}

    # 3) Create a new membership row (normal member, not admin)
    membership = GroupMembership(
        group_id=group_id,
        user_id=current_user.id,
        is_admin=False,  # creator is admin, normal join is a regular member
    )

    db.add(membership)

    try:
        db.commit()
    except IntegrityError:
        # In case of a race condition or duplicate insert, ensure DB is clean
        db.rollback()
        return {"detail": Messages.ALREADY_MEMBER}

    return {"detail": "Joined group successfully"}



def leave_group(db: Session, group_id: int, current_user: User) -> dict:

    _get_group_or_404(db, group_id)

    membership = db.query(GroupMembership).filter(
        GroupMembership.group_id == group_id,
        GroupMembership.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Messages.NOT_A_MEMBER,
        )

    db.delete(membership)
    db.commit()
    return {"detail": "Left group successfully"}


# ===========================
# ADDED: Story 8 — Posts (List / Create)
# ===========================
def list_group_posts(db: Session, group_id: int, current_user: User) -> List[GroupPost]:

    _get_group_or_404(db, group_id)

    if not _is_member(db, group_id, current_user.id):  
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Messages.MUST_JOIN_TO_VIEW,
        )

    posts = (
        db.query(GroupPost)
        .filter(GroupPost.group_id == group_id)
        .order_by(GroupPost.created_at.desc())
        .all()
    )
    return posts

def create_group_post(db: Session, group_id: int, post_in: GroupPostCreate, current_user: User) -> GroupPost:
    """
    Grupta yeni post oluşturur. Sadece üyeler post atabilir.
    """
    _get_group_or_404(db, group_id)

    if not _is_member(db, group_id, current_user.id):  
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Messages.MUST_JOIN_TO_POST,
        )

    post = GroupPost(
        content=post_in.content,
        group_id=group_id,
        user_id=current_user.id,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post



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
            detail=Messages.GROUP_NOT_ADMIN,
        )

    # 2) Load the group from the database
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if db_group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Messages.GROUP_NOT_FOUND,
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

def list_group_members(
    db: Session,
    group_id: int,
    current_user: User,
) -> list[GroupMemberRead]:
    """
    Return all members of a group as GroupMemberRead objects.
    """

    # 1) Check if the group exists
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if db_group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Messages.GROUP_NOT_FOUND,
        )

    # (Optional) Here you could check if current_user is a member
    # or admin before listing members, if you want stricter rules.

    # 2) Get all memberships for this group, including user info
    memberships = (
        db.query(GroupMembership)
        .filter(GroupMembership.group_id == group_id)
        .join(GroupMembership.user)
        .all()
    )

    # 3) Map memberships to GroupMemberRead objects
    members_read: list[GroupMemberRead] = [
        GroupMemberRead(
            user_id=m.user_id,
            username=m.user.username,
            is_admin=m.is_admin,
            created_at=m.created_at,
        )
        for m in memberships
    ]

    return members_read




def remove_group_member(
    db: Session,
    group_id: int,
    user_id: int,
    current_user: User,
) -> None:
    """
    Remove a member from a group.
    Only group admins are allowed to do this.
    """

    # 1) Check that the group exists
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if db_group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Messages.GROUP_NOT_FOUND,
        )

    # 2) Check that the current user is an admin in this group
    membership_admin = (
        db.query(GroupMembership)
        .filter(
            GroupMembership.group_id == group_id,
            GroupMembership.user_id == current_user.id,
        )
        .first()
    )

    if membership_admin is None or not membership_admin.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Messages.GROUP_NOT_ADMIN, 
        )

    # 3) Find the membership to remove
    membership_to_remove = (
        db.query(GroupMembership)
        .filter(
            GroupMembership.group_id == group_id,
            GroupMembership.user_id == user_id,
        )
        .first()
    )

    if membership_to_remove is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Messages.GROUP_MEMBER_NOT_FOUND,
        )

    # 4) Delete the membership and commit
    db.delete(membership_to_remove)
    db.commit()
    # 5) No return value is needed (204 No Content in the endpoint)
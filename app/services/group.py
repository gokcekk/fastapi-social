# app/services/group.py

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.exc import IntegrityError

from app.models.group import Group, GroupPost 
from app.models.user import User
from app.schemas.group import GroupMemberRead, GroupUpdate, GroupPostCreate    
from app.models.group_membership import GroupMembership

from app.services.group_helpers import get_group_or_404, is_member, is_user_admin_in_group



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
    get_group_or_404(db, group_id)

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
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already a member of this group.",
    )

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
        return {"detail": "You are already a member of this group."}

    return {"detail": "Joined the group successfully."}




def leave_group(db: Session, group_id: int, current_user: User) -> dict:

    get_group_or_404(db, group_id)

    membership = db.query(GroupMembership).filter(
        GroupMembership.group_id == group_id,
        GroupMembership.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not a member of this group.",
    )


    db.delete(membership)
    db.commit()
    return {"detail": "Left the group successfully."}


# ===========================
# ADDED: Story 8 — Posts (List / Create)
# ===========================
def list_group_posts(
        db: Session, 
        group_id: int, 
        current_user: User
        ) -> List[GroupPost]:

    get_group_or_404(db, group_id)

    if not is_member(db, group_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must join the group to view posts.",
    )



    posts = (
        db.query(GroupPost)
        .filter(GroupPost.group_id == group_id)
        .order_by(GroupPost.created_at.desc())
        .all()
    )
    return posts

def create_group_post(
        db: Session, 
        group_id: int, 
        post_in: GroupPostCreate, 
        current_user: User
        ) -> GroupPost:

    get_group_or_404(db, group_id)

    if not is_member(db, group_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must join the group to create a post.",
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





def update_group(
    db: Session,
    group_id: int,
    group_in: GroupUpdate,
    current_user: User,
) -> Group:
    """
    Update a group's name/description if the current user is an admin.
    """

    # 2) Load the group from the database
    db_group = get_group_or_404(db, group_id)

    # 1) Check if current_user is admin in this group
    is_admin = is_user_admin_in_group(
        db=db,
        group_id=group_id,
        current_user=current_user,
    )
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group admins can update this group.",
    )



    # 3) Update fields only if they are provided
    if group_in.name is not None:                #group_in: new from client 
        db_group.name = group_in.name            #db_group: old from db

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
    get_group_or_404(db, group_id)

    # (Optional) Here you could check if current_user is a member
    # or admin before listing members, if you want stricter rules.
    if not is_member(db, group_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must join the group to view members.",
    )




    # 2) Get all memberships for this group, including user info
    memberships = (
        db.query(GroupMembership)
        .filter(GroupMembership.group_id == group_id)
        .join(GroupMembership.user)
        .all()
    )

    # 3) Map memberships to GroupMemberRead objects
    members_read = []

    for m in memberships:
     member = GroupMemberRead(
        user_id=m.user_id,
        username=m.user.username,
        is_admin=m.is_admin,
        created_at=m.created_at,
    )
     members_read.append(member)

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
    get_group_or_404(db, group_id)

    # 2) Check that the current user is an admin in this group
    is_admin = is_user_admin_in_group(db=db, group_id=group_id, current_user=current_user)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group admins can perform this action.",
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
            detail="Group member not found.",
    )


    # 4) Delete the membership and commit
    db.delete(membership_to_remove)
    db.commit()
    return
    


# app/routers/group.py
"""
Group endpoints for Story 6 and Story 8.

IMPORTANT:
- For Story 6 (basic group CRUD) we kept most logic in this router,
- For Story 8 (admin operations, membership rules, etc.) we moved
  the business logic into app.services.group and call it from here.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.group import Group, GroupPost
from app.models.group_membership import GroupMembership
from app.schemas.group import (
    GroupOut,
    GroupCreate,
    GroupUpdate,
    GroupMemberRead,
    GroupPostCreate,
    GroupPostOut,
)
from app.models.user import User
from app.core.auth import get_current_user

# Service layer for Story 8 and membership logic
from app.services.group import (
    update_group,
    list_group_members,
    remove_group_member,
    join_group as svc_join_group,
    leave_group as svc_leave_group,
    list_group_posts as svc_list_group_posts,
    create_group_post as svc_create_group_post,
)

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
)


"""ST-6.0: Create a new group."""
@router.post(
    "/",
    response_model=GroupOut,
    status_code=status.HTTP_201_CREATED,
)
def create_group(
    group_in: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # creator must become admin
):
    """
    Create a new group and make the current user an admin member.

    NOTE:
    - This still contains some business logic (creation + membership).
      We did NOT move it into the service layer yet, to keep your
      teammate's Story 6 code closer to the original design.
    - If you want full consistency later, you can extract this
      into a create_group service function.
    """

    # 1) Check if there is a group with the same name
    existing = db.query(Group).filter(Group.name == group_in.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A group with this name already exist",
        )

    # 2) Create the group row
    group = Group(
        name=group_in.name,
        description=group_in.description,
        owner_id=current_user.id,
    )

    db.add(group)
    db.commit()
    db.refresh(group)

    # 3) Create a membership row for the creator as admin
    membership = GroupMembership(
        group_id=group.id,
        user_id=current_user.id,
        is_admin=True,
    )

    db.add(membership)
    db.commit()

    return group


"""ST-6.2: The endpoint that lists all groups."""
@router.get(
        "/", 
        response_model=list[GroupOut])
def list_groups(
    db: Session = Depends(get_db),
):
    """
    Return all groups.

    This is a simple read-only endpoint; keeping it in the router is fine.
    """
    groups = db.query(Group).all()
    return groups


"""ST-6.3: Bring the detail of a single group."""
@router.get(
        "/{group_id}", 
        response_model=GroupOut
        )
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
):
    """
    Return one group by id, or 404 if it does not exist.
    """
    group = db.query(Group).filter(Group.id == group_id).first()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found",
        )
    return group


"""ST-6.4: Current user joins this group."""
@router.post(
    "/{group_id}/join",
    status_code=status.HTTP_200_OK,
)
def join_group_endpoint(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Current authenticated user joins the given group.

    - We delegate the real logic to the service layer (svc_join_group).
    - Service handles:
        * 404 if group does not exist
        * "already member" check
        * membership insert + commit
    """
    return svc_join_group(
        db=db,
        group_id=group_id,
        current_user=current_user,
    )


"""ST-6.5: Current user is left from this group."""
@router.post(
    "/{group_id}/leave",
    status_code=status.HTTP_200_OK,
)
def leave_group_endpoint(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Current authenticated user leaves the given group.

    - Old version used `current_user.groups` (direct many-to-many).
    - Now we use the GroupMembership-based logic in the service.
    - Service handles:
        * 404 if group does not exist
        * 400 if user is not a member
        * membership delete + commit
    """
    return svc_leave_group(
        db=db,
        group_id=group_id,
        current_user=current_user,
    )


"""ST-6.7: List posts in this group."""
@router.get(
    "/{group_id}/posts",
    response_model=list[GroupPostOut],
    status_code=status.HTTP_200_OK,
)
def list_group_posts_endpoint(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all posts in a group.

    - Only group members are allowed to see the posts.
    - Membership + 403 logic lives in svc_list_group_posts.
    """
    return svc_list_group_posts(
        db=db,
        group_id=group_id,
        current_user=current_user,
    )


"""ST-6.8: Current user creates a new post in this group."""
@router.post(
    "/{group_id}/posts",
    response_model=GroupPostOut,
    status_code=status.HTTP_201_CREATED,
)
def create_group_post_endpoint(
    group_id: int,
    post_in: GroupPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new post in the given group.

<<<<<<< HEAD
    - Only group members are allowed to create posts.
    - Membership + 403 logic lives in svc_create_group_post.
    """
    return svc_create_group_post(
        db=db,
        group_id=group_id,
        post_in=post_in,
        current_user=current_user,
    )


# =========================
# User Story 8 (admin ops)
# =========================

@router.put(
    "/{group_id}",
    response_model=GroupOut,
    status_code=status.HTTP_200_OK,
)
def update_group_endpoint(
    group_id: int,
    group_update: GroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update group name/description.

    - Real admin check is inside the update_group service.
    - If current_user is not an admin, service raises 403.
    """
    return update_group(
        group_id=group_id,
        group_in=group_update,
        db=db,
        current_user=current_user,
    )


@router.get(
    "/{group_id}/members",
    response_model=list[GroupMemberRead],
    status_code=status.HTTP_200_OK,
)
def list_group_members_endpoint(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all members of a group.

    - Service returns a list of GroupMemberRead objects.
    - You can later add extra access rules (only admins, etc.)
      inside the service function.
    """
    return list_group_members(
        db=db,
        group_id=group_id,
        current_user=current_user,
    )


@router.delete(
    "/{group_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_members_from_groups(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Remove a user from a group.

    - Only admins are allowed to do this.
    - Service checks:
        * group exists (404)
        * current user is admin (403)
        * target member exists (404)
    """
    remove_group_member(
        group_id=group_id,
        user_id=user_id,
        db=db,
        current_user=current_user,
    )
    # 204 No Content: nothing is returned in the body
    return
=======
   return group_post




#User Story 8
>>>>>>> develop

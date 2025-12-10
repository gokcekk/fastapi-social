# app/routers/groups.py


# TODO: Replace or clean up this temporary implementation from story 6 later.

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.group import Group
from app.schemas.group import GroupCreate, GroupRead, GroupUpdate, GroupMemberRead
from app.services.group import create_group, update_group, list_group_members, remove_group_member

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
)

# TEMP for local testing, will be removed
# Story 6


@router.post(
    "/",
    response_model=GroupRead,
    status_code=status.HTTP_201_CREATED,
)
def create_group_endpoint (
    group_in : GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user), #creator must become admin

):
    return create_group(
        db=db, 
        group_in=group_in,
        current_user=current_user,
        )


# Story 8

@router.put(
    "/{group_id}",
    response_model=GroupRead,
    status_code=status.HTTP_200_OK,
)
def update_group_endpoint(
    group_id: int,
    group_update: GroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)

):
    return update_group(
        group_id=group_id,
        group_in=group_update,
        db=db,
        current_user=current_user,

    )

@router.get(
    "/{group_id}/members",
    response_model=list[GroupMemberRead], 
    status_code=status.HTTP_200_OK
    
)
def list_group_members_endpoint (
    group_id: int,
    db:Session= Depends(get_db),
    current_user:User = Depends(get_current_user),

):
    return list_group_members(
        db=db,
        group_id=group_id,
        current_user=current_user,
    )

@router.delete(
    "/{group_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)

def remove_members_from_groups (
    group_id:int,
    user_id:int,
    db:Session= Depends(get_db),
    current_user:User = Depends(get_current_user),

):
    return remove_group_member (
        group_id=group_id,
        user_id=user_id,
        db=db,
        current_user=current_user,
    )
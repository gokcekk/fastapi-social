from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.group import Group, GroupPost
from app.models.group import Group
from app.schemas.group import GroupOut,GroupPostOut,GroupPostCreate,GroupCreate
from app.models.user import User
from app.routers.auth import get_current_user


router = APIRouter(
    prefix="/groups",
    tags=["groups"],
)


"""ST-6.0: Create a new group."""
@router.post("/", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
def create_group(
   group_in: GroupCreate,
   db:Session = Depends(get_db),
):
#check if there is a group with the same name
     existing =db.query(Group).filter(Group.name == group_in.name).first()
     if existing:
        raise HTTPException (
           status_code=status.HTTP_400_BAD_REQUEST,
           detail="A group with this name already exist",

        )
     
     group = Group(
        name=group_in.name,
        description=group_in.description,
     )

     db.add(group)
     db.commit()
     db.refresh(group)

     return group

"""ST-6.2: The endpoint that lists all groups."""

@router.get("/",response_model=list[GroupOut])
def list_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    groups = db.query(Group).all()
    return groups

"""ST-6.3: Bring the detail of a single group."""
@router.get("/{group_id}", response_model=GroupOut)
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   group = db.query(Group).filter(Group.id == group_id).first()

   if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found",
        )
   return group
   
# @router.get("/{group_id}", response_model=GroupOut)
# def get_group(
#     group_id:int,
#     db: Session = Depends(get_db),
# ):

"""ST-6.4: Current user joins this group."""

@router.post("/{group_id}/join")    
def join_group(
    group_id:int,
    db:Session = Depends(get_db),
    current_user: User = Depends(get_current_user)

):
    
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
       raise HTTPException(
           status_code = status.HTTP_404_NOT_FOUND,
           detail = "Group not found",
       )
    if group in current_user.groups:
      return {"detail": "Already a member of this group"}
    
    current_user.groups.append(group)
    db.commit()
    return {"detail": "Joined group successfully"}

"""ST-6.5: Current user is left from this group."""
@router.post("/{group_id}/leave")    
def leave_group(
      group_id: int,
      db:Session = Depends(get_db),
      current_user: User = Depends(get_current_user),
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
       raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail="Group not found"
       )
    if group not in current_user.groups:
       raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail="You are not a member of this group",
       )
    current_user.groups.remove(group)
    db.commit()
    return{"detail":"Left group successfully"}

"""ST-6.7: List posts in this group."""
@router.get("/{group_id}/posts",response_model=list[GroupPostOut])
def list_group_posts(
   group_id:int,
   db: Session = Depends(get_db),
   current_user: User = Depends(get_current_user),
): 
   
   group = db.query(Group).filter(Group.id == group_id).first()
   if not group:
      raise HTTPException(
         status_code=status.HTTP_404_NOT_FOUND,
         detail="Group not found"
      )
   #only group members can see the posts
   if group not in current_user.groups:
      raise HTTPException(
         status_code=status.HTTP_403_FORBIDDEN,
         detail="You must join the group to see its posts"
      )
   posts=(
      db.query(GroupPost)
      .filter(GroupPost.group_id ==group_id)
      .order_by(GroupPost.created_at.desc())
      .all()
   )
   return posts


"""ST-6.8: Current user creates a new post in this group."""
@router.post(
   "/{group_id}/posts",
   response_model=GroupPostOut,
   status_code=status.HTTP_201_CREATED,
)
def create_group_post(
   group_id:int,
   post_in: GroupPostCreate,
   db:Session=Depends(get_db),
   current_user: User = Depends(get_current_user)

):
   group = db.query(Group).filter(Group.id == group_id).first()
   if not group:
      raise HTTPException(
         status_code=status.HTTP_404_NOT_FOUND,
         detail = 'Group not found',
        
      )
   # If the user is not a member of this group, he should not post
   if group not in current_user.groups:
      raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must join the group to create posts",
      )
   group_post = GroupPost(
        content=post_in.content,
        group_id=group_id,
        user_id=current_user.id,
    )
    
   db.add(group_post)
   db.commit()
   db.refresh(group_post)

   return group_post
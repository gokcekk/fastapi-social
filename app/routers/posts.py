# app/routers/posts.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.posts import Post as PostModel
from app.schemas.posts import Post as PostSchema, PostCreate
from app.core.auth import get_current_user
from app.models.user import User
from app.models.friend_request import FriendRequest, RequestStatus


router = APIRouter(
    prefix="/post",
    tags=["posts"],
)


@router.post("/", response_model=PostSchema, status_code=status.HTTP_201_CREATED)
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new post"""
    db_post = PostModel(
        content=post.content,
        user_id=current_user.id,
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.get("/me", response_model=list[PostSchema])
def read_my_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get only the logged in user's posts"""
    return (
        db.query(PostModel)
        .filter(PostModel.user_id == current_user.id)
        .order_by(PostModel.created_at.desc())
        .all()
    )


@router.get("/feed", response_model=list[PostSchema])
def read_friends_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get posts from approved friends only"""

    # Get list of friend's user_ids
    approved_requests = db.query(FriendRequest).filter(
    FriendRequest.status == RequestStatus.approved,
    (
        (FriendRequest.from_user_id == current_user.id) |
        (FriendRequest.to_user_id == current_user.id)
    )
    ).all()

    friend_ids = [
        fr.to_user_id if fr.from_user_id == current_user.id else fr.from_user_id
        for fr in approved_requests
    ]

    if not friend_ids:
        return []  # user has no friends yet

    return (
        db.query(PostModel)
        .filter(PostModel.user_id.in_(friend_ids))
        .order_by(PostModel.created_at.desc())
        .all()
    )


@router.get("/", response_model=list[PostSchema])
def read_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all posts"""
    # Show user + friends posts together
    approved_requests = db.query(FriendRequest).filter(
    FriendRequest.status == RequestStatus.approved,
    (
        (FriendRequest.from_user_id == current_user.id) |
        (FriendRequest.to_user_id == current_user.id)
    )
    ).all()

    friend_ids = [
        fr.to_user_id if fr.from_user_id == current_user.id else fr.from_user_id
        for fr in approved_requests
    ]
    allowed_ids = friend_ids + [current_user.id]

    return (
        db.query(PostModel)
        .filter(PostModel.user_id.in_(allowed_ids))
        .order_by(PostModel.created_at.desc())
        .all()
    )


@router.get("/{post_id}", response_model=PostSchema)
def read_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    """Get a post by id"""
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.put("/{post_id}", response_model=PostSchema)
def update_post(
    post_id: int,
    updated_post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a post"""
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post not found")

    # Only the owner can edit this post
    if post.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not allowed to edit this post")

    post.content = updated_post.content
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a post"""
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post not found")

    # Only the owner can delete this post
    if post.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not allowed to delete this post")

    db.delete(post)
    db.commit()



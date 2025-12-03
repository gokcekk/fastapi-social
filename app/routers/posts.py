# app/routers/posts.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.posts import Post as PostModel
from app.schemas.posts import Post as PostSchema, PostCreate
from app.core.auth import get_current_user
from app.models.user import User



router = APIRouter(
    prefix="/post",
    tags=["posts"],
)


@router.get("/", response_model=list[PostSchema])
def read_posts(
    db: Session = Depends(get_db)
    
    ):
    """Get all posts"""
    return db.query(PostModel).all()


@router.post("/", response_model=PostSchema)
def create_post(
    post: PostCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
 
    ):
    """Create a new post"""
    db_post = PostModel(user=post.user, content=post.content)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.get("/{post_id}", response_model=PostSchema)
def read_post(post_id: int, db: Session = Depends(get_db)):
    """Get a post by id"""
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/{post_id}", response_model=PostSchema)
def update_post(post_id: int, updated_post: PostCreate, db: Session = Depends(get_db)):
    """Update a post"""
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.content = updated_post.content
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """Delete a post"""
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"detail": "Post deleted"}

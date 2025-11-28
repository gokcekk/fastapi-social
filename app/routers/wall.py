from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

"""We create a router, to connect the endpoints in this file to the app"""
router = APIRouter(
    prefix="/wall",       # All endpoints under this router will be /wall/...
    tags=["Wall"]         # Category tag on Swagger /docs page
)

""" Endpoint: View posts on the user's own wall"""
@router.get("/{user_id}", response_model=list[schemas.Post])
def get_user_wall(user_id: int, db: Session = Depends(get_db)):
    """
    Returns all posts on the user's own wall.
    - user_id: Which user's wall will be displayed.
    - db: Database session (we retrieve it with dependency)
    """
    """First we check if the user exists"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        """If the user does not exist, a 404 error is returned"""
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    """ We get all posts of the user, sort them by creation date (newest on top)"""
    posts = (
        db.query(models.Post)
        .filter(models.Post.user_id == user_id)
        .order_by(models.Post.created_at.desc())
        .all()
    )
    return posts

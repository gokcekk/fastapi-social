# app/routers/auth.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserCreate, UserRead, UserLogin
from app.schemas.auth import Token
from app.services.auth import create_user, login_user
from app.core.auth import get_current_user
from app.models.user import User
from fastapi.security.oauth2 import OAuth2PasswordRequestForm


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

#test
@router.post(
        "/register", 
        response_model=UserRead,
        status_code=status.HTTP_201_CREATED,)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """Register a new user account."""
    user = create_user(db=db, user_in=user_in)
    return user



@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user_in = UserLogin(
        username=form_data.username,
        password=form_data.password,
    )
    return login_user(db=db, user_in=user_in)



@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Log out the current user.

    With JWT, real logout happens on the client side by deleting the token.
    This endpoint just validates the token and tells the client to remove it.
    """
    return {"detail": "Logged out successfully. Please remove the token on the client side."}
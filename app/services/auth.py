# app/services/auth.py

from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.schemas.auth import Token


def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Create a new user with a hashed password.

    Steps:
    1. Check if username is already taken.
    2. Check if email is already registered.
    3. Hash the plain password.
    4. Create and save the User in the database.
    5. Return the created User object.
    """

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_in.username).first()
    if existing_user:
        # If the username is taken, return a 400 Bad Request error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken.",
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_in.email).first()
    if existing_email:
        # If the email is already used, return a 400 Bad Request error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )

    # Hash the plain password before storing it in the database
    hashed_pw = hash_password(user_in.password)

    # Create the User ORM object (not yet saved to the database)
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hashed_pw,
    )

    # Persist the new user in the database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Reload the object with any DB-generated fields (e.g. id)

    return db_user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """
    Verify username and password.

    Steps:
    1. Look up the user by username.
    2. If user does not exist, return None.
    3. If password does not match the stored hash, return None.
    4. If both are valid, return the User object.

    This function does NOT raise HTTP exceptions.
    It only returns:
      - User  -> when credentials are correct
      - None  -> when credentials are invalid
    """
    # Try to find a user with the given username
    user = db.query(User).filter(User.username == username).first()
    if not user:
        # Username not found
        return None

    # Check if the provided password matches the stored hashed password
    if not verify_password(password, user.password_hash):
        # Password is incorrect
        return None

    # Both username and password are valid
    return user


def login_user(db: Session, user_in: UserLogin) -> Token:
    """
    Authenticate the user and return a JWT access token.

    Steps:
    1. Use authenticate_user to check credentials.
    2. If credentials are invalid, raise a 400 error.
    3. If valid, create a JWT access token with the username as "sub".
    4. Wrap the token in a Token schema and return it.

    This function is typically called from the /auth/login endpoint.
    """
    # Check if the username and password are correct
    user = authenticate_user(db, user_in.username, user_in.password)
    if not user:
        # If authentication fails, inform the client
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password.",
        )

    # Define how long the token should be valid
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Create the JWT access token.
    # We include the username in the "sub" (subject) claim.
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    # Return a Token schema instance.
    # token_type will default to "bearer" as defined in Token.
    return Token(access_token=access_token)

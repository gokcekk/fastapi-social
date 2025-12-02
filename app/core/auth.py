# app/core/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.user import User

# OAuth2PasswordBearer:
# - Tells FastAPI that we use "Bearer <token>" in the Authorization header
# - tokenUrl is used in the Swagger UI "Authorize" button
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency that returns the current authenticated user.

    How it works:
    1. Reads the JWT access token from the Authorization header
       using oauth2_scheme.
    2. Decodes the token using SECRET_KEY and ALGORITHM.
    3. Extracts the username from the "sub" claim.
    4. Looks up the user in the database.
    5. If anything fails, raises a 401 Unauthorized error.
    """

    # Prepare a reusable exception for invalid or missing credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT token:
        # - token: the string from "Authorization: Bearer <token>"
        # - SECRET_KEY and ALGORITHM are used to verify the signature
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Get the username from the "sub" claim in the token payload
        # "sub" usually means "subject", the identity of the token owner
        username: str | None = payload.get("sub")

        # If there is no "sub" in the token, the token is not valid
        if username is None:
            raise credentials_exception

    except JWTError:
        # Any error while decoding:
        # - token expired
        # - wrong signature
        # - corrupted token
        # We treat all of these as invalid credentials
        raise credentials_exception

    # Query the database for a user with this username
    user = db.query(User).filter(User.username == username).first()

    # If no such user exists in the database, credentials are invalid
    if user is None:
        raise credentials_exception

    # If everything is fine, return the User object.
    # FastAPI will inject this into endpoints that depend on get_current_user.
    return user

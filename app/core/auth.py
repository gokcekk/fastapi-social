# app/core/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.user import User
from app.core.messages import Messages

# OAuth2PasswordBearer:
# - Tells FastAPI that we use "Bearer <token>" in the Authorization header
# - tokenUrl is used in the Swagger UI "Authorize" button
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency that returns the current authenticated user.

    Steps:
    1. Read the JWT access token from the Authorization header using oauth2_scheme.
    2. Decode the token with SECRET_KEY and ALGORITHM.
    3. Get the username from the "sub" claim.
    4. Look up the user in the database.
    5. If any step fails, raise a 401 Unauthorized error.
    """

    # Reusable exception for all "invalid credentials" cases
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=Messages.CREDENTIALS_NOT_VALID,
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT token from "Authorization: Bearer <token>"
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Get the username from the "sub" (subject) claim
        username: str | None = payload.get("sub")

        # If there is no "sub", the token is not valid
        if username is None:
            raise credentials_exception

    except JWTError:
        # Any error while decoding the token:
        # - expired token
        # - invalid signature
        # - malformed token
        # All are treated as invalid credentials
        raise credentials_exception

    # Look up the user in the database
    user = db.query(User).filter(User.username == username).first()

    # If no user exists with this username, credentials are invalid
    if user is None:
        raise credentials_exception

    # If everything is OK, return the User object
    return user

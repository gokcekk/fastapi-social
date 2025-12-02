# app/core/security.py

from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

# Password hashing configuration
# This object knows:
# - Which hashing algorithm to use (bcrypt)
# - How to verify a password against a hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
# SECRET_KEY:
#   - Used to sign the JWT
#   - Must be kept secret in a real application (env variable, not in code)
# ALGORITHM:
#   - The cryptographic algorithm for signing the token (HS256 is HMAC with SHA256)
# ACCESS_TOKEN_EXPIRE_MINUTES:
#   - How long the token is valid (here: 60 minutes)
SECRET_KEY = "super_secret_key_change_me"  # For learning only, change in real apps
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60000000000000000000000000000000000000000000000000000


def hash_password(password: str) -> str:
    """
    Hash the plain password using bcrypt.

    Usage:
    - Called when a new user is created (register).
    - We never store the plain password in the database.
    - We only store the hashed version.

    Example:
        hashed = hash_password("my_plain_password")
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Usage:
    - Called during login.
    - Compares the plain password from the user
      with the hashed password stored in the database.

    Returns:
    - True  if the password is correct
    - False if it is not
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    Parameters:
    - data: a dictionary with the data we want to encode in the token.
      Commonly, we include:
        {"sub": username}
      where "sub" (subject) is the identity of the user.

    - expires_delta: an optional timedelta for the expiration time.
      If provided, we use it.
      If not provided, we use the default ACCESS_TOKEN_EXPIRE_MINUTES.

    What this function does:
    1. Copies the input data.
    2. Calculates the expiration datetime (UTC).
    3. Adds the "exp" (expiration) claim to the payload.
    4. Uses jose.jwt.encode to create a signed JWT string.

    Returns:
    - A string that represents the JWT access token.

    Example:
        from datetime import timedelta

        token = create_access_token(
            data={"sub": "ronaldo"},
            expires_delta=timedelta(minutes=30)
        )
    """
    # Make a copy so we do not modify the original dictionary
    to_encode = data.copy()

    # Determine the expiration time
    if expires_delta:
        # Use the custom expiration if given
        expire = datetime.utcnow() + expires_delta
    else:
        # Otherwise, use the default configured lifetime
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Add the expiration claim to the payload
    to_encode.update({"exp": expire})

    # Encode the token:
    # - to_encode: payload (for example {"sub": "username", "exp": ...})
    # - SECRET_KEY: used to sign the token
    # - ALGORITHM: defines how the token is signed (HS256)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Return the signed JWT string
    return encoded_jwt

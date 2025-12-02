# app/schemas/auth.py

from pydantic import BaseModel


class Token(BaseModel):
    """
    Schema for the authentication token returned after a successful login.

    Used in:
    - POST /api/v1/auth/login  (response_model=Token)

    Fields:
    - access_token: The actual JWT string that the client must send
      in the Authorization header for protected endpoints.
      Example:
        "Authorization: Bearer <access_token_here>"

    - token_type: The type of token. Usually "bearer" for OAuth2/JWT.
      We set a default value "bearer", so we don't need to provide
      it every time we create a Token object in the code.
    """
    # The JWT access token string
    access_token: str
    #note
    # The type of the token, usually "bearer"
    # Default value is set here, so when we create Token(...),
    # we only need to pass access_token.
    token_type: str = "bearer"

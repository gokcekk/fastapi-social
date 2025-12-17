# app.routers.users

## Endpoints
- GET /users/me
  - Returns the currently authenticated user profile.
  - Depends on get_current_user.

- PUT /users/me
  - Updates current user's profile fields (display_name, bio, avatar_url) if provided.
  - Depends on get_db and get_current_user.
  - Commits and refreshes the user.

## Test strategy
Router unit tests:
- Override get_current_user with a fake user object
- Override get_db with a fake session that records add/commit/refresh calls
- No real database used

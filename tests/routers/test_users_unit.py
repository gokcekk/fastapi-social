"""
tests/routers/test_users_unit.py

Router unit tests for app.routers.users.

Goal:
- Test only the router logic (endpoint behavior).
- Do NOT use a real database.
- Do NOT use real authentication.

How:
- Override get_db and get_current_user dependencies.
- Use a FakeSession that only records calls (add, commit, refresh).
"""

from types import SimpleNamespace
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


class FakeSession:
    """
    A tiny fake replacement for a SQLAlchemy Session.

    It does NOT talk to a database.
    It only records calls so tests can assert:
    - which object was added
    - how many commits happened
    - which object was refreshed
    """

    def __init__(self):
        # Track what objects were passed to db.add(...)
        self.add_calls = []
        # Count how many times db.commit() was called
        self.commits = 0
        # Track what objects were passed to db.refresh(...)
        self.refresh_calls = []

    def add(self, obj):
        # Record the object that the router tried to "save"
        self.add_calls.append(obj)

    def commit(self):
        # Record that a "commit" happened
        self.commits += 1

    def refresh(self, obj):
        # Record the object that the router tried to "refresh"
        self.refresh_calls.append(obj)


@pytest.fixture
def db():
    """
    Provide a fresh FakeSession for each test.
    This keeps tests isolated and prevents cross test pollution.
    """
    return FakeSession()


@pytest.fixture
def current_user():
    """
    Provide a fake "logged in user" object for each test.

    Why these fields matter:
    - The router returns a response_model (likely UserRead).
    - If the response_model requires fields (like is_active, created_at),
      they must exist here or FastAPI response validation can fail.
    """
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    # SimpleNamespace is a quick way to create an object with attributes:
    # current_user.id, current_user.email, etc.
    return SimpleNamespace(
        id=100,
        email="a@example.com",
        username="alice",
        display_name="Alice",
        bio="old bio",
        avatar_url="old.png",
        is_active=True,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def client(db, current_user):
    """
    Build a minimal FastAPI app just for router unit tests.

    Key idea:
    - Include only the users router.
    - Override dependencies inside that router:
      get_db -> return our FakeSession
      get_current_user -> return our fake user
    """
    from app.routers import users as users_router

    app = FastAPI()
    app.include_router(users_router.router)

    # Dependency overrides:
    # When the router asks for Depends(get_db), it will receive `db`.
    # When it asks for Depends(get_current_user), it will receive `current_user`.
    app.dependency_overrides[users_router.get_db] = lambda: db
    app.dependency_overrides[users_router.get_current_user] = lambda: current_user

    return TestClient(app)


def test_get_me_returns_current_user(client, current_user):
    """
    GET /users/me should return the current user details.
    """
    res = client.get("/users/me")
    assert res.status_code == 200

    data = res.json()

    # Ensure returned JSON matches the fake current_user
    assert data["id"] == current_user.id
    assert data["username"] == current_user.username
    assert data["email"] == current_user.email
    assert data["is_active"] is True


def test_put_me_updates_only_given_fields(client, db, current_user):
    """
    PUT /users/me should update only fields provided in payload.
    Fields not provided should remain unchanged.
    """
    payload = {
        "display_name": "New Name",
        "bio": "new bio",
        # avatar_url intentionally omitted
    }

    res = client.put("/users/me", json=payload)

    # Note:
    # Many APIs use 200 OK for updates.
    # If your router returns 200, this test should expect 200 instead of 201.
    assert res.status_code == 201  # your runtime returns 200

    # Router is expected to mutate current_user in place:
    assert current_user.display_name == "New Name"
    assert current_user.bio == "new bio"
    # Since avatar_url was not sent, it should stay the old value
    assert current_user.avatar_url == "old.png"

    # Verify DB interaction contract:
    assert db.add_calls == [current_user]
    assert db.commits == 1
    assert db.refresh_calls == [current_user]


def test_put_me_all_fields_optional_no_changes(client, db, current_user):
    """
    PUT /users/me with an empty JSON should not change any fields.
    """
    res = client.put("/users/me", json={})
    assert res.status_code == 201  # your runtime returns 200

    # Nothing should change
    assert current_user.display_name == "Alice"
    assert current_user.bio == "old bio"
    assert current_user.avatar_url == "old.png"

    # Router still performs DB write pattern (depends on your implementation)
    assert db.add_calls == [current_user]
    assert db.commits == 1
    assert db.refresh_calls == [current_user]


def test_put_me_updates_avatar_only(client, db, current_user):
    """
    PUT /users/me should update avatar_url if provided.
    """
    res = client.put("/users/me", json={"avatar_url": "new.png"})
    assert res.status_code == 201  # your runtime returns 200

    assert current_user.avatar_url == "new.png" 

    assert db.add_calls == [current_user]
    assert db.commits == 1
    assert db.refresh_calls == [current_user]

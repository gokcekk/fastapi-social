"""
tests/routers/test_users_unit.py

Router unit tests for app.routers.users:
- Overrides get_current_user and get_db
- Uses a fake in memory session (no real DB)
"""

from types import SimpleNamespace
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


class FakeSession:
    def __init__(self):
        self.add_calls = []
        self.commits = 0
        self.refresh_calls = []

    def add(self, obj):
        self.add_calls.append(obj)

    def commit(self):
        self.commits += 1

    def refresh(self, obj):
        self.refresh_calls.append(obj)


@pytest.fixture
def db():
    return FakeSession()


@pytest.fixture
def current_user():
    # Must contain required fields from UserRead (at least is_active + created_at)
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    return SimpleNamespace(
        id=100,
        email="a@example.com",
        username="alice",
        display_name="Alice",
        bio="old bio",
        avatar_url="old.png",
        is_active=True,     # required by your UserRead
        created_at=now,     # required by your UserRead
        updated_at=now,
    )


@pytest.fixture
def client(db, current_user):
    from app.routers import users as users_router

    app = FastAPI()
    app.include_router(users_router.router)

    # override dependencies used inside app/routers/users.py
    app.dependency_overrides[users_router.get_db] = lambda: db
    app.dependency_overrides[users_router.get_current_user] = lambda: current_user

    return TestClient(app)


def test_get_me_returns_current_user(client, current_user):
    res = client.get("/users/me")
    assert res.status_code == 200

    data = res.json()
    assert data["id"] == current_user.id
    assert data["username"] == current_user.username
    assert data["email"] == current_user.email
    assert data["is_active"] is True


def test_put_me_updates_only_given_fields(client, db, current_user):
    payload = {
        "display_name": "New Name",
        "bio": "new bio",
        # avatar_url omitted on purpose
    }

    res = client.put("/users/me", json=payload)
    assert res.status_code == 200  # your runtime returns 200

    # router mutates current_user in place
    assert current_user.display_name == "New Name"
    assert current_user.bio == "new bio"
    assert current_user.avatar_url == "old.png"

    # DB calls
    assert db.add_calls == [current_user]
    assert db.commits == 1
    assert db.refresh_calls == [current_user]


def test_put_me_all_fields_optional_no_changes(client, db, current_user):
    res = client.put("/users/me", json={})
    assert res.status_code == 200  # your runtime returns 200

    assert current_user.display_name == "Alice"
    assert current_user.bio == "old bio"
    assert current_user.avatar_url == "old.png"

    assert db.add_calls == [current_user]
    assert db.commits == 1
    assert db.refresh_calls == [current_user]


def test_put_me_updates_avatar_only(client, db, current_user):
    res = client.put("/users/me", json={"avatar_url": "new.png"})
    assert res.status_code == 200  # your runtime returns 200

    assert current_user.avatar_url == "new.png"

    assert db.add_calls == [current_user]
    assert db.commits == 1
    assert db.refresh_calls == [current_user]

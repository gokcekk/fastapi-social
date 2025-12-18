"""
tests/routers/test_auth_unit.py

Unit tests for app.routers.auth
- No real DB
- Overrides get_db and get_current_user
- Monkeypatches service functions create_user / login_user
"""

from types import SimpleNamespace
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient


class FakeSession:
    pass


@pytest.fixture
def db():
    return FakeSession()


@pytest.fixture
def current_user():
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
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
def app(db, current_user):
    from app.routers import auth as auth_router

    app = FastAPI()
    app.include_router(auth_router.router)

    # override dependencies used in router
    app.dependency_overrides[auth_router.get_db] = lambda: db
    app.dependency_overrides[auth_router.get_current_user] = lambda: current_user

    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_register_calls_create_user_and_returns_user(client, monkeypatch, db):
    from app.routers import auth as auth_router

    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    fake_user = SimpleNamespace(
        id=1,
        email="new@example.com",
        username="newuser",
        display_name=None,
        bio=None,
        avatar_url=None,
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    called = {"count": 0, "db": None, "payload": None}

    def fake_create_user(*, db, user_in):
        called["count"] += 1
        called["db"] = db
        called["payload"] = user_in
        return fake_user

    # patch the imported function in router module
    monkeypatch.setattr(auth_router, "create_user", fake_create_user)

    payload = {
        "email": "new@example.com",
        "username": "newuser",
        "password": "Secret123!",
    }

    res = client.post("/auth/register", json=payload)
    assert res.status_code == status.HTTP_201_CREATED

    data = res.json()
    assert data["id"] == 1
    assert data["email"] == "new@example.com"
    assert data["username"] == "newuser"
    assert data["is_active"] is True

    assert called["count"] == 1
    assert called["db"] is db
    assert called["payload"].email == "new@example.com"
    assert called["payload"].username == "newuser"


def test_login_returns_token(client, monkeypatch, db):
    from app.routers import auth as auth_router

    called = {"count": 0, "db": None, "payload": None}

    def fake_login_user(*, db, user_in):
        called["count"] += 1
        called["db"] = db
        called["payload"] = user_in
        return {"access_token": "fake.jwt.token", "token_type": "bearer"}

    monkeypatch.setattr(auth_router, "login_user", fake_login_user)

    # OAuth2PasswordRequestForm expects form-encoded data
    res = client.post(
        "/auth/login",
        data={"username": "alice", "password": "Secret123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert res.status_code == 200

    data = res.json()
    assert data["access_token"] == "fake.jwt.token"
    assert data["token_type"] == "bearer"

    assert called["count"] == 1
    assert called["db"] is db
    assert called["payload"].username == "alice"
    assert called["payload"].password == "Secret123!"


def test_logout_requires_auth_and_returns_message(client):
    # get_current_user is overridden to always return a user,
    # so logout should succeed.
    res = client.post("/auth/logout")
    assert res.status_code == status.HTTP_204_NO_CONTENT
    assert res.content == b""

"""
tests/routers/test_auth_unit.py

Router unit tests for app.routers.auth:
- Overrides get_db and get_current_user
- Mocks create_user and login_user service functions
"""

from types import SimpleNamespace
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient

import app.routers.auth as auth_router_module


class FakeSession:
    """Minimal fake db session object for router tests."""
    pass


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(auth_router_module.router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def db():
    return FakeSession()


@pytest.fixture(autouse=True)
def override_db(app, db):
    def _get_db():
        return db

    app.dependency_overrides[auth_router_module.get_db] = _get_db
    yield
    app.dependency_overrides.pop(auth_router_module.get_db, None)


@pytest.fixture
def mock_create_user(monkeypatch):
    called = {}

    def fake_create_user(*, db, user_in):
        called["db"] = db
        called["user_in"] = user_in

        now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        # Return something that response_model (UserRead) can serialize
        return SimpleNamespace(
            id=1,
            username=getattr(user_in, "username", "alice"),
            email=getattr(user_in, "email", "a@example.com"),
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    monkeypatch.setattr(auth_router_module, "create_user", fake_create_user)
    return called


@pytest.fixture
def mock_login_user(monkeypatch):
    called = {}

    def fake_login_user(*, db, user_in):
        called["db"] = db
        called["user_in"] = user_in
        return {"access_token": "test-token", "token_type": "bearer"}

    monkeypatch.setattr(auth_router_module, "login_user", fake_login_user)
    return called


def test_register_success(client, mock_create_user):
    payload = {
        "username": "alice",
        "email": "a@example.com",
        "password": "secret123",
    }

    res = client.post("/auth/register", json=payload)

    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["id"] == 1
    assert data["username"] == "alice"
    assert data["email"] == "a@example.com"

    assert "user_in" in mock_create_user
    assert mock_create_user["user_in"].username == "alice"
    assert mock_create_user["user_in"].email == "a@example.com"


def test_register_validation_error(client):
    # Missing required fields -> FastAPI/Pydantic should return 422
    res = client.post("/auth/register", json={})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_success(client, mock_login_user):
    # OAuth2PasswordRequestForm uses form data (x-www-form-urlencoded)
    res = client.post(
        "/auth/login",
        data={"username": "alice", "password": "secret123"},
    )

    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["access_token"] == "test-token"
    assert data["token_type"] == "bearer"

    assert "user_in" in mock_login_user
    assert mock_login_user["user_in"].username == "alice"


def test_login_validation_error_missing_form_fields(client):
    res = client.post("/auth/login", data={})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_logout_success(app, client):
    def override_get_current_user():
        return SimpleNamespace(id=1, username="alice", email="a@example.com")

    app.dependency_overrides[auth_router_module.get_current_user] = override_get_current_user

    res = client.post("/auth/logout")
    assert res.status_code == status.HTTP_200_OK
    assert "detail" in res.json()

    app.dependency_overrides.pop(auth_router_module.get_current_user, None)


def test_logout_unauthorized(app, client):
    def override_get_current_user():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    app.dependency_overrides[auth_router_module.get_current_user] = override_get_current_user

    res = client.post("/auth/logout")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

    app.dependency_overrides.pop(auth_router_module.get_current_user, None)

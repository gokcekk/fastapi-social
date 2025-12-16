"""
tests/routers/test_group_unit.py

Router unit test for app.routers.group:
- Overrides get_db and get_current_user
- Uses a fake in memory DB
- Patches Group and GroupMembership models used inside router
"""

from types import SimpleNamespace
from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


class DummyColumn:
    """Mimic SQLAlchemy column behavior for '==' in filters."""
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other):
        return (self.name, "==", other)


class FakeGroup:
    id = DummyColumn("id")
    name = DummyColumn("name")

    def __init__(self, name: str, description: str | None, owner_id: int):
        self.id = None
        self.name = name
        self.description = description
        self.owner_id = owner_id
        self.created_at = datetime(2025, 1, 1, 12, 0, 0)


class FakeMembership:
    def __init__(self, group_id: int, user_id: int, is_admin: bool):
        self.group_id = group_id
        self.user_id = user_id
        self.is_admin = is_admin


class FakeQuery:
    def __init__(self, model, store):
        self.model = model
        self.store = store
        self._conds = []

    def filter(self, *conds):
        self._conds.extend(list(conds))
        return self

    def first(self):
        if self.model is FakeGroup:
            for cond in self._conds:
                if isinstance(cond, tuple) and len(cond) == 3:
                    field, op, value = cond
                    if field == "name" and op == "==":
                        return next((g for g in self.store["groups"] if g.name == value), None)
                    if field == "id" and op == "==":
                        return next((g for g in self.store["groups"] if g.id == value), None)
        return None

    def all(self):
        if self.model is FakeGroup:
            return list(self.store["groups"])
        return []


class FakeSession:
    def __init__(self):
        self.store = {"groups": [], "next_group_id": 1}
        self._added = []

    def query(self, model):
        return FakeQuery(model, self.store)

    def add(self, obj):
        self._added.append(obj)
        if isinstance(obj, FakeGroup):
            if obj.id is None:
                obj.id = self.store["next_group_id"]
                self.store["next_group_id"] += 1
            self.store["groups"].append(obj)

    def commit(self):
        return None

    def refresh(self, obj):
        return None


@pytest.fixture
def db():
    return FakeSession()


@pytest.fixture
def current_user():
    return SimpleNamespace(id=100, username="alice")


@pytest.fixture
def client(db, current_user, monkeypatch):
    from app.routers import group as group_router

    monkeypatch.setattr(group_router, "Group", FakeGroup)
    monkeypatch.setattr(group_router, "GroupMembership", FakeMembership)

    app = FastAPI()
    app.include_router(group_router.router)

    app.dependency_overrides[group_router.get_db] = lambda: db
    app.dependency_overrides[group_router.get_current_user] = lambda: current_user

    return TestClient(app)


def test_group_flow(client):
    create_resp = client.post(
        "/groups/",
        json={"name": "My Group", "description": "hello"},
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["name"] == "My Group"
    group_id = created["id"]

    list_resp = client.get("/groups/")
    assert list_resp.status_code == 200
    groups = list_resp.json()
    assert any(g["id"] == group_id for g in groups)

    detail_resp = client.get(f"/groups/{group_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == group_id

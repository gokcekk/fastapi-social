# tests/services/test_group_service.py

"""
Module: app.services.group

Unit tests for group service functions.
We mock the SQLAlchemy Session and patch helper functions.
We also patch SQLAlchemy models (GroupMembership, GroupPost) with fake classes
to avoid SQLAlchemy mapper configuration during unit tests.
"""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.services import group as group_service
from app.core.exaption_messages import Messages
from app.core.exceptions import ForbiddenError, BadRequestError, NotFoundError
from app.schemas.group import GroupUpdate, GroupPostCreate


class DummyColumn:
    """Mimic SQLAlchemy column behavior for '==' in filters."""
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other):
        # Any object is fine, MagicMock filter accepts it.
        return (self.name, "==", other)


class FakeMembership:
    # Mimic SQLAlchemy model class attributes used in query filters
    group_id = DummyColumn("group_id")
    user_id = DummyColumn("user_id")

    def __init__(self, group_id: int, user_id: int, is_admin: bool):
        self.group_id = group_id
        self.user_id = user_id
        self.is_admin = is_admin


class FakeGroupPost:
    def __init__(self, content: str, group_id: int, user_id: int):
        self.content = content
        self.group_id = group_id
        self.user_id = user_id
        self.created_at = None


@pytest.fixture
def db() -> Session:
    return MagicMock(spec=Session)


@pytest.fixture
def current_user():
    return SimpleNamespace(id=100, username="alice")


@pytest.fixture
def group_id():
    return 55


# ---------- join_group ----------
def test_join_group_returns_already_member_when_exists(db, current_user, group_id, monkeypatch):
    monkeypatch.setattr(group_service, "get_group_or_404", lambda db, group_id: object())

    db.query.return_value.filter.return_value.first.return_value = SimpleNamespace()

    result = group_service.join_group(db=db, group_id=group_id, current_user=current_user)

    assert result == {"detail": Messages.ALREADY_MEMBER}
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_join_group_creates_membership_when_not_member(db, current_user, group_id, monkeypatch):
    monkeypatch.setattr(group_service, "get_group_or_404", lambda db, group_id: object())
    monkeypatch.setattr(group_service, "GroupMembership", FakeMembership)

    db.query.return_value.filter.return_value.first.return_value = None

    result = group_service.join_group(db=db, group_id=group_id, current_user=current_user)

    assert result == {"detail": Messages.GROUP_JOIN_SUCCESS}

    db.add.assert_called_once()
    added_obj = db.add.call_args[0][0]
    assert isinstance(added_obj, FakeMembership)
    assert added_obj.group_id == group_id
    assert added_obj.user_id == current_user.id
    assert added_obj.is_admin is False

    db.commit.assert_called_once()


def test_join_group_integrity_error_is_idempotent(db, current_user, group_id, monkeypatch):
    monkeypatch.setattr(group_service, "get_group_or_404", lambda db, group_id: object())
    monkeypatch.setattr(group_service, "GroupMembership", FakeMembership)

    db.query.return_value.filter.return_value.first.return_value = None
    db.commit.side_effect = IntegrityError("stmt", {}, Exception("orig"))

    result = group_service.join_group(db=db, group_id=group_id, current_user=current_user)

    assert result == {"detail": Messages.ALREADY_MEMBER}
    db.rollback.assert_called_once()


# ---------- leave_group ----------
def test_leave_group_raises_when_not_member(db, current_user, group_id, monkeypatch):
    monkeypatch.setattr(group_service, "get_group_or_404", lambda db, group_id: object())

    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(BadRequestError) as exc:
        group_service.leave_group(db=db, group_id=group_id, current_user=current_user)

    assert Messages.NOT_A_MEMBER in str(exc.value)


def test_leave_group_deletes_membership(db, current_user, group_id, monkeypatch):
    monkeypatch.setattr(group_service, "get_group_or_404", lambda db, group_id: object())

    membership = SimpleNamespace(id=1)
    db.query.return_value.filter.return_value.first.return_value = membership

    result = group_service.leave_group(db=db, group_id=group_id, current_user=current_user)

    assert result == {"detail": Messages.GROUP_LEAVE_SUCCESS}
    db.delete.assert_called_once_with(membership)
    db.commit.assert_called_once()


# ---------- list_group_posts ----------
def test_list_group_posts_forbidden_when_not_member(db, current_user, group_id, monkeypatch):
    monkeypatch.setattr(group_service, "get_group_or_404", lambda db, group_id: object())
    monkeypatch.setattr(group_service, "is_member", lambda db, group_id, user_id: False)

    with pytest.raises(ForbiddenError) as exc:
        group_service.list_group_posts(db=db, group_id=group_id, current_user=current_user)

    assert Messages.MUST_JOIN_TO_VIEW in str(exc.value)


def test_list_group_posts_returns_posts_when_member(db, current_user, group_id, monkeypatch):
    monkeypatch.setattr(group_service, "get_group_or_404", lambda db, group_id: object())
    monkeypatch.setattr(group_service, "is_member", lambda db, group_id, user_id: True)

    fake_posts = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = fake_posts

    posts = group_service.list_group_posts(db=db, group_id=group_id, current_user=current_user)

    assert posts == fake_posts


# ---------- create_group_post ----------
def test_create_group_post_forbidden_when_not_member(db, current_user, group_id, monkeypatch):
    monkeypatch.setattr(group_service, "get_group_or_404", lambda db, group_id: object())
    monkeypatch.setattr(group_service, "is_member", lambda db, group_id, user_id: False)

    with pytest.raises(ForbiddenError) as exc:
        group_service.create_group_post(
            db=db,
            group_id=group_id,
            post_in=GroupPostCreate(content="hello"),
            current_user=current_user,
        )

    assert Messages.MUST_JOIN_TO_POST in str(exc.value)


def test_create_group_post_creates_post_when_member(db, current_user, group_id, monkeypatch):
    monkeypatch.setattr(group_service, "get_group_or_404", lambda db, group_id: object())
    monkeypatch.setattr(group_service, "is_member", lambda db, group_id, user_id: True)
    monkeypatch.setattr(group_service, "GroupPost", FakeGroupPost)

    post_in = GroupPostCreate(content="hello")

    result = group_service.create_group_post(
        db=db,
        group_id=group_id,
        post_in=post_in,
        current_user=current_user,
    )

    assert isinstance(result, FakeGroupPost)
    assert result.content == "hello"
    assert result.group_id == group_id
    assert result.user_id == current_user.id

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


# ---------- update_group ----------
def test_update_group_forbidden_when_not_admin(db, current_user, group_id, monkeypatch):
    fake_group = SimpleNamespace(id=group_id, name="Old", description="Old desc")

    monkeypatch.setattr(group_service, "get_group_or_404", lambda db, group_id: fake_group)
    monkeypatch.setattr(group_service, "is_user_admin_in_group", lambda db, group_id, current_user: False)

    with pytest.raises(ForbiddenError) as exc:
        group_service.update_group(
            db=db,
            group_id=group_id,
            group_in=GroupUpdate(name="New", description=None),
            current_user=current_user,
        )

    assert Messages.GROUP_NOT_ADMIN in str(exc.value)


def test_update_group_updates_fields_when_admin(db, current_user, group_id, monkeypatch):
    fake_group = SimpleNamespace(id=group_id, name="Old", description="Old desc")

    monkeypatch.setattr(group_service, "get_group_or_404", lambda db, group_id: fake_group)
    monkeypatch.setattr(group_service, "is_user_admin_in_group", lambda db, group_id, current_user: True)

    updated = group_service.update_group(
        db=db,
        group_id=group_id,
        group_in=GroupUpdate(name="NewName", description="NewDesc"),
        current_user=current_user,
    )

    assert updated.name == "NewName"
    assert updated.description == "NewDesc"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(fake_group)


# ---------- list_group_members ----------
def test_list_group_members_forbidden_when_not_member(db, current_user, group_id, monkeypatch):
    monkeypatch.setattr(group_service, "get_group_or_404", lambda db, group_id: object())
    monkeypatch.setattr(group_service, "is_member", lambda db, group_id, user_id: False)

    with pytest.raises(ForbiddenError) as exc:
        group_service.list_group_members(db=db, group_id=group_id, current_user=current_user)

    assert Messages.MUST_JOIN_TO_VIEW in str(exc.value)


def test_list_group_members_maps_to_schema(db, current_user, group_id, monkeypatch):
    monkeypatch.setattr(group_service, "get_group_or_404", lambda db, group_id: object())
    monkeypatch.setattr(group_service, "is_member", lambda db, group_id, user_id: True)

    dt = datetime(2025, 1, 1, 12, 0, 0)
    memberships = [
        SimpleNamespace(
            user_id=1,
            user=SimpleNamespace(username="u1"),
            is_admin=True,
            created_at=dt,
        ),
        SimpleNamespace(
            user_id=2,
            user=SimpleNamespace(username="u2"),
            is_admin=False,
            created_at=dt,
        ),
    ]

    db.query.return_value.filter.return_value.join.return_value.all.return_value = memberships

    result = group_service.list_group_members(db=db, group_id=group_id, current_user=current_user)

    assert len(result) == 2
    assert result[0].username == "u1"
    assert result[0].is_admin is True
    assert result[1].username == "u2"
    assert result[1].is_admin is False


# ---------- remove_group_member ----------
def test_remove_group_member_requires_admin(db, current_user, group_id, monkeypatch):
    monkeypatch.setattr(group_service, "get_group_or_404", lambda db, group_id: object())
    monkeypatch.setattr(group_service, "is_user_admin_in_group", lambda db, group_id, current_user: False)

    with pytest.raises(ForbiddenError) as exc:
        group_service.remove_group_member(
            db=db,
            group_id=group_id,
            user_id=999,
            current_user=current_user,
        )

    assert Messages.GROUP_NOT_ADMIN in str(exc.value)


def test_remove_group_member_raises_when_target_missing(db, current_user, group_id, monkeypatch):
    monkeypatch.setattr(group_service, "get_group_or_404", lambda db, group_id: object())
    monkeypatch.setattr(group_service, "is_user_admin_in_group", lambda db, group_id, current_user: True)

    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(NotFoundError) as exc:
        group_service.remove_group_member(
            db=db,
            group_id=group_id,
            user_id=999,
            current_user=current_user,
        )

    assert Messages.GROUP_MEMBER_NOT_FOUND in str(exc.value)


def test_remove_group_member_deletes_when_found(db, current_user, group_id, monkeypatch):
    monkeypatch.setattr(group_service, "get_group_or_404", lambda db, group_id: object())
    monkeypatch.setattr(group_service, "is_user_admin_in_group", lambda db, group_id, current_user: True)

    membership = SimpleNamespace(id=1)
    db.query.return_value.filter.return_value.first.return_value = membership

    group_service.remove_group_member(
        db=db,
        group_id=group_id,
        user_id=2,
        current_user=current_user,
    )

    db.delete.assert_called_once_with(membership)
    db.commit.assert_called_once()

#python -m pytest -q tests\services\test_group_service.py

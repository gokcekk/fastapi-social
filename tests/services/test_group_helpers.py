# tests/services/test_group_helpers.py

"""
Module: app.services.group_helpers

Tests in this file are unit tests.
We mock the SQLAlchemy Session so we don't need a real database.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.services.group_helpers import (
    get_group_or_404,
    is_member,
    is_user_admin_in_group,
)
from app.core.exaption_messages import Messages
from app.core.exceptions import NotFoundError
from app.models.group import Group
from app.models.group_membership import GroupMembership


# ---------- helpers ----------
def _assert_error_message(exc: Exception, expected: str) -> None:
    """
    Your custom exceptions might store message in .detail or only in str(exc).
    This helper supports both.
    """
    detail = getattr(exc, "detail", None)
    if detail is not None:
        assert detail == expected
    else:
        assert expected in str(exc)


# ---------- fixtures ----------
@pytest.fixture
def db() -> Session:
    """Mocked SQLAlchemy Session."""
    return MagicMock(spec=Session)


@pytest.fixture
def current_user():
    """Fake current user object with id field."""
    return SimpleNamespace(id=7, username="alice")


# ---------- tests: get_group_or_404 ----------
def test_get_group_or_404_returns_group_when_found(db):
    fake_group = SimpleNamespace(id=1)

    db.query.return_value.filter.return_value.first.return_value = fake_group

    result = get_group_or_404(db=db, group_id=1)

    assert result is fake_group
    db.query.assert_called_once_with(Group)


def test_get_group_or_404_raises_not_found_when_missing(db):
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(NotFoundError) as exc:
        get_group_or_404(db=db, group_id=999)

    _assert_error_message(exc.value, Messages.GROUP_NOT_FOUND)


# ---------- tests: is_member ----------
def test_is_member_returns_true_when_membership_exists(db):
    db.query.return_value.filter.return_value.first.return_value = SimpleNamespace()

    assert is_member(db=db, group_id=10, user_id=20) is True
    db.query.assert_called_once_with(GroupMembership)


def test_is_member_returns_false_when_no_membership(db):
    db.query.return_value.filter.return_value.first.return_value = None

    assert is_member(db=db, group_id=10, user_id=20) is False


# ---------- tests: is_user_admin_in_group ----------
def test_is_user_admin_in_group_returns_false_when_no_membership(db, current_user):
    db.query.return_value.filter.return_value.first.return_value = None

    assert is_user_admin_in_group(db=db, group_id=1, current_user=current_user) is False


def test_is_user_admin_in_group_returns_false_when_membership_not_admin(db, current_user):
    membership = SimpleNamespace(is_admin=False)
    db.query.return_value.filter.return_value.first.return_value = membership

    assert is_user_admin_in_group(db=db, group_id=1, current_user=current_user) is False


def test_is_user_admin_in_group_returns_true_when_admin(db, current_user):
    membership = SimpleNamespace(is_admin=True)
    db.query.return_value.filter.return_value.first.return_value = membership

    assert is_user_admin_in_group(db=db, group_id=1, current_user=current_user) is True

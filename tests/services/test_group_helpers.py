# tests/services/test_group_helpers.py

"""
Module: app.services.group_helpers

Unit tests (no real DB).
We mock the SQLAlchemy Session using MagicMock.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.group import Group
from app.models.group_membership import GroupMembership
from app.services.group_helpers import (
    get_group_or_404,
    is_member,
    is_user_admin_in_group,
)


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

    with pytest.raises(HTTPException) as exc:
        get_group_or_404(db=db, group_id=999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Group not found."


# ---------- tests: is_member ----------
def test_is_member_returns_true_when_membership_exists(db):
    db.query.return_value.filter.return_value.first.return_value = SimpleNamespace()

    assert is_member(db=db, group_id=10, user_id=20) is True
    db.query.assert_called_once_with(GroupMembership)


def test_is_member_returns_false_when_no_membership(db):
    db.query.return_value.filter.return_value.first.return_value = None

    assert is_member(db=db, group_id=10, user_id=20) is False
    db.query.assert_called_once_with(GroupMembership)


# ---------- tests: is_user_admin_in_group ----------
def test_is_user_admin_in_group_returns_false_when_no_membership(db, current_user):
    db.query.return_value.filter.return_value.first.return_value = None

    assert is_user_admin_in_group(db=db, group_id=1, current_user=current_user) is False
    db.query.assert_called_once_with(GroupMembership)


def test_is_user_admin_in_group_returns_false_when_membership_not_admin(db, current_user):
    membership = SimpleNamespace(is_admin=False)
    db.query.return_value.filter.return_value.first.return_value = membership

    assert is_user_admin_in_group(db=db, group_id=1, current_user=current_user) is False
    db.query.assert_called_once_with(GroupMembership)


def test_is_user_admin_in_group_returns_true_when_admin(db, current_user):
    membership = SimpleNamespace(is_admin=True)
    db.query.return_value.filter.return_value.first.return_value = membership

    assert is_user_admin_in_group(db=db, group_id=1, current_user=current_user) is True
    db.query.assert_called_once_with(GroupMembership)

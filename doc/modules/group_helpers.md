# app.services.group_helpers

## Purpose
Small reusable helper functions for group services.

## Functions
### get_group_or_404(db, group_id) -> Group
* Queries Group by id
* Raises NotFoundError if group does not exist
* Returns Group if found

### is_member(db, group_id, user_id) -> bool
* Checks if a GroupMembership row exists for the given user in the group

### is_user_admin_in_group(db, group_id, current_user) -> bool
* Reads GroupMembership for current_user in the group
* Returns True only if membership exists and is_admin is True

## Test strategy
Unit tests mock the SQLAlchemy Session.
No real DB, fast feedback.

## Run tests
From project root:

```bash
python -m pytest -q tests/services/test_group_helpers.py

# app.services.group

## Purpose
Business logic for group features:
- join/leave groups
- list/create posts
- update group details
- list members
- remove member (admin-only)

## Dependencies
This module uses helpers from `app.services.group_helpers`:
- get_group_or_404
- is_member
- is_user_admin_in_group

## Test strategy
Unit tests:
- mock SQLAlchemy Session
- patch helper functions to focus only on service logic
- validate return values, raised exceptions, and db method calls

## Run tests
From project root:

```bash
python -m pytest -q tests/services/test_group_service.py

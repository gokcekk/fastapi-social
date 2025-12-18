# app.routers.group

## Purpose
Defines HTTP endpoints for group features (Story 6 and Story 8).

Story 6:
- create_group (router contains some business logic)
- list_groups
- get_group
- join_group_endpoint (delegates to service)
- leave_group_endpoint (delegates to service)
- list_group_posts_endpoint (delegates to service)
- create_group_post_endpoint (delegates to service)

Story 8:
- update_group_endpoint (delegates to service)
- list_group_members_endpoint (delegates to service)
- remove_members_from_groups (delegates to service, returns 204)

## Dependencies
- get_db dependency (SQLAlchemy Session)
- get_current_user dependency (authentication)

## Test strategy
Router tests:
- override dependencies (db and current_user)
- patch service layer functions to isolate router behavior
- patch SQLAlchemy models used inside router functions (Group, GroupMembership)
  to avoid SQLAlchemy mapper configuration in unit tests

## Run tests
From project root:

```bash
python -m pytest -q tests/routers/test_group.py

from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.models.user import User
from app.models.group import Group, GroupPost
from app.routers.auth import get_current_user

def override_get_current_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email=="testuser@example.com").first()
        if not user:
            user = User(
                username = "testuser",
                email = "testuser@example.com",
                password_hash = "test-hash",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()

app.dependency_overrides[get_current_user] = override_get_current_user
client = TestClient(app)

def test_group_flow():

    #create group


    #list group
    list_resp = client.get("/groups")
    assert list_resp.status_code == 200
    groups = list_resp.json()
    assert any(g["id"] == group_id for g in groups)

    #get group detail
    detail_resp = client.get(f"/groups/{group_id}")
    assert detail_resp.status_code == 200
    group_detail = detail_resp.json()
    assert group_detail["id"] == group_id
    assert group_detail["name"] == "test-group"

    #join the group
    join_resp = client.post(f"/groups/{group_id}/join")
    assert join_resp.status_code == 200
    assert "Joined" in join_resp.json()["detail"]

    #create post in the group
    post_creatte_resp = client.post(
        f"/groups/{group_id}/posts",
        json = {"content":"hello from test post"},
    )
    assert post_creatte_resp.status_code == 201
    post_data = post_creatte_resp.json()
    assert post_data["group_id"] == group_id
    assert post_data["content"] == "hello from test post"

    #list posts in the group
    posts_list_resp = client.get(f"/groups/{group_id}/posts")
    assert posts_list_resp.status_code == 200
    posts = posts_list_resp.json()
    assert len(posts) >= 1
    assert any(p["id"] == post_data["id"] for p in posts)

    #leave group
    leave_resp = client.post(f"/groups/{group_id}/leave")
    assert leave_resp.status_code == 200
    assert "Left"in leave_resp.json()["detail"]


from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db
from uuid import uuid4

# Create a temporary test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)


# Dependency override for DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Create a helper function to create a user + login
def create_test_user():
    unique = str(uuid4())[:8]

    user_data = {
        "username": f"alice_{unique}",
        "email": f"alice_{unique}@example.com",
        "password": "password123"
    }

    # Register
    res = client.post("/auth/register", json=user_data)
    print("REGISTER RESPONSE:", res.status_code, res.json())   # Debug
    assert res.status_code in (200, 201)

    # Login with username (NOT email)
    login_res = client.post("/auth/login", data={
        "username": user_data["username"],   # FIXED
        "password": user_data["password"]
    })

    print("LOGIN RESPONSE:", login_res.status_code, login_res.json())  # Debug
    assert login_res.status_code == 200

    token = login_res.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}

# Test creating a post
def test_create_post():
    headers = create_test_user()

    data = {"content": "Hello world!"}

    response = client.post("/post", json=data, headers=headers)
    assert response.status_code == 201
    assert response.json()["content"] == "Hello world!"

# Test getting posts
def test_get_posts():
    headers = create_test_user()

    # Create one post
    client.post("/post", json={"content": "My post"}, headers=headers)

    # Fetch all posts
    response = client.get("/post", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


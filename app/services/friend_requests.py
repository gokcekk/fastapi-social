<<<<<<< Updated upstream
<<<<<<< Updated upstream:app/routers/user_activities.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Social Network - Friend Requests")

# --- Simple in-memory data storage (instead of a real database) ---
users = {}  # user_id -> user_name
friend_requests = []  # {from_id, to_id, status}
friends = {}  # user_id -> [friend_ids]


# --- Models ---
class UserCreate(BaseModel):
    user_id: int
    name: str


class FriendRequestCreate(BaseModel):
    from_id: int
    to_id: int


class FriendRequestResponse(BaseModel):
    request_id: int
    action: str  # "approve" or "deny"


# --- Create a new user ---
@app.post("/users")
def create_user(user: UserCreate):
=======
from fastapi import HTTPException
from typing import Dict, List

from app.schemas.friend_requests import (
    UserCreate,
    FriendRequestCreate,
    FriendRequestResponse,
)

# --- In-memory (temporary) database ---
users: Dict[int, str] = {}   # user_id -> user_name
friends: Dict[int, List[int]] = {}  # user_id -> list of friend_ids
friend_requests: List[Dict] = []     # friend request list


def create_user_service(user: UserCreate):
>>>>>>> Stashed changes:app/services/friend_requests.py
=======
from fastapi import HTTPException
from typing import Dict, List

from app.schemas.friend_requests import (
    UserCreate,
    FriendRequestCreate,
    FriendRequestResponse,
)

# --- In-memory (temporary) database ---
users: Dict[int, str] = {}   # user_id -> user_name
friends: Dict[int, List[int]] = {}  # user_id -> list of friend_ids
friend_requests: List[Dict] = []     # friend request list


def create_user_service(user: UserCreate):
>>>>>>> Stashed changes
    if user.user_id in users:
        raise HTTPException(status_code=400, detail="User already exists")

    users[user.user_id] = user.name
    friends[user.user_id] = []
    return {"message": "User created", "user": user}


<<<<<<< Updated upstream
<<<<<<< Updated upstream:app/routers/user_activities.py
# --- Send a friend request ---
@app.post("/friend-request")
def send_friend_request(req: FriendRequestCreate):
=======
=======
>>>>>>> Stashed changes
def send_friend_request_service(req: FriendRequestCreate):

>>>>>>> Stashed changes:app/services/friend_requests.py
    if req.from_id not in users or req.to_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    if req.to_id in friends[req.from_id]:
<<<<<<< Updated upstream:app/routers/user_activities.py
        raise HTTPException(status_code=400, detail="Already friends")
=======
        raise HTTPException(status_code=400, detail="You are already friends")

    # Duplicate check
    for fr in friend_requests:
        if fr["from_id"] == req.from_id and fr["to_id"] == req.to_id and fr["status"] == "pending":
            raise HTTPException(status_code=400, detail="Friend request already sent")
>>>>>>> Stashed changes:app/services/friend_requests.py

    friend_requests.append({
        "id": len(friend_requests),
        "from_id": req.from_id,
        "to_id": req.to_id,
        "status": "pending"
    })

    return {"message": "Friend request sent!"}


<<<<<<< Updated upstream
<<<<<<< Updated upstream:app/routers/user_activities.py
# --- Get incoming friend requests for a user ---
@app.get("/friend-request/{user_id}")
def get_friend_requests(user_id: int):
    incoming = [fr for fr in friend_requests if fr["to_id"] == user_id and fr["status"] == "pending"]
    return {"incoming_requests": incoming}


# --- Respond to a friend request (approve or deny) ---
@app.post("/friend-request/respond")
def respond_request(response: FriendRequestResponse):
    # Check if request exists
=======
=======
>>>>>>> Stashed changes
def get_incoming_requests_service(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    incoming = [
        fr for fr in friend_requests
        if fr["to_id"] == user_id and fr["status"] == "pending"
    ]

    return {
        "user_id": user_id,
        "incoming_requests": incoming,
        "count": len(incoming)
    }


def respond_request_service(response: FriendRequestResponse):

>>>>>>> Stashed changes:app/services/friend_requests.py
    if response.request_id >= len(friend_requests):
        raise HTTPException(status_code=404, detail="Friend request not found")

    fr = friend_requests[response.request_id]

    if fr["status"] != "pending":
        raise HTTPException(status_code=400, detail="Request already handled")

    if response.action not in ["approve", "deny"]:
        raise HTTPException(status_code=400, detail="Invalid action")

<<<<<<< Updated upstream
<<<<<<< Updated upstream:app/routers/user_activities.py
    # Approve the request
=======
>>>>>>> Stashed changes:app/services/friend_requests.py
=======
>>>>>>> Stashed changes
    if response.action == "approve":
        friends[fr["from_id"]].append(fr["to_id"])
        friends[fr["to_id"]].append(fr["from_id"])
        fr["status"] = "approved"
        return {"message": "Friend request approved"}

<<<<<<< Updated upstream
<<<<<<< Updated upstream:app/routers/user_activities.py
    # Deny the request
=======
>>>>>>> Stashed changes:app/services/friend_requests.py
=======
>>>>>>> Stashed changes
    fr["status"] = "denied"
    return {"message": "Friend request denied"}

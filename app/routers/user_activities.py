from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Social Network - Friend Request System")

# --- In-memory (temporary) database ---
users: Dict[int, str] = {}   # user_id -> user_name
friends: Dict[int, List[int]] = {}  # user_id -> list of friend_ids
friend_requests: List[Dict] = []     # list of friend request dicts


# --- Pydantic Models ---
class UserCreate(BaseModel):
    user_id: int
    name: str


class FriendRequestCreate(BaseModel):
    from_id: int
    to_id: int


class FriendRequestResponse(BaseModel):
    request_id: int
    action: str  # approve or deny


# -------------------------
# USER MANAGEMENT
# -------------------------
@app.post("/users", summary="Create a new user", tags=["Users"])
def create_user(user: UserCreate):
    if user.user_id in users:
        raise HTTPException(status_code=400, detail="User already exists")

    users[user.user_id] = user.name
    friends[user.user_id] = []

    return {
        "message": "User created successfully",
        "user": {"id": user.user_id, "name": user.name}
    }


# -------------------------
# SEND FRIEND REQUEST
# -------------------------
@app.post("/friend-request", summary="Send a friend request", tags=["Friend Requests"])
def send_friend_request(req: FriendRequestCreate):

    if req.from_id not in users or req.to_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    if req.from_id == req.to_id:
        raise HTTPException(status_code=400, detail="Cannot send request to yourself")

    if req.to_id in friends[req.from_id]:
        raise HTTPException(status_code=400, detail="You are already friends")

    # Check if request already exists
    for fr in friend_requests:
        if fr["from_id"] == req.from_id and fr["to_id"] == req.to_id and fr["status"] == "pending":
            raise HTTPException(status_code=400, detail="Friend request already sent")

    friend_requests.append({
        "id": len(friend_requests),
        "from_id": req.from_id,
        "to_id": req.to_id,
        "status": "pending"
    })

    return {"message": "Friend request sent successfully"}



# GET INCOMING REQUESTS

@app.get("/friend-request/{user_id}", summary="Get incoming friend requests", tags=["Friend Requests"])
def get_friend_requests(user_id: int):

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


# -------------------------
# APPROVE OR DENY REQUEST
# -------------------------
@app.post("/friend-request/respond", summary="Respond to a friend request", tags=["Friend Requests"])
def respond_request(response: FriendRequestResponse):

    if response.request_id >= len(friend_requests):
        raise HTTPException(status_code=404, detail="Friend request not found")

    fr = friend_requests[response.request_id]

    if fr["status"] != "pending":
        raise HTTPException(status_code=400, detail="Request already processed")

    if response.action not in ["approve", "deny"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    # Approve request
    if response.action == "approve":
        friends[fr["from_id"]].append(fr["to_id"])
        friends[fr["to_id"]].append(fr["from_id"])
        fr["status"] = "approved"

        return {"message": "Friend request approved"}

    # Deny request
    fr["status"] = "denied"
    return {"message": "Friend request denied"}

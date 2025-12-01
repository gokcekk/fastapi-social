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
    if user.user_id in users:
        raise HTTPException(status_code=400, detail="User already exists")

    users[user.user_id] = user.name
    friends[user.user_id] = []
    return {"message": "User created", "user": user}


# --- Send a friend request ---
@app.post("/friend-request")
def send_friend_request(req: FriendRequestCreate):
    if req.from_id not in users or req.to_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    if req.to_id in friends[req.from_id]:
        raise HTTPException(status_code=400, detail="Already friends")

    friend_requests.append({
        "id": len(friend_requests),
        "from_id": req.from_id,
        "to_id": req.to_id,
        "status": "pending"
    })

    return {"message": "Friend request sent!"}


# --- Get incoming friend requests for a user ---
@app.get("/friend-request/{user_id}")
def get_friend_requests(user_id: int):
    incoming = [fr for fr in friend_requests if fr["to_id"] == user_id and fr["status"] == "pending"]
    return {"incoming_requests": incoming}


# --- Respond to a friend request (approve or deny) ---
@app.post("/friend-request/respond")
def respond_request(response: FriendRequestResponse):
    # Check if request exists
    if response.request_id >= len(friend_requests):
        raise HTTPException(status_code=404, detail="Friend request not found")

    fr = friend_requests[response.request_id]

    if fr["status"] != "pending":
        raise HTTPException(status_code=400, detail="Request already handled")

    if response.action not in ["approve", "deny"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    # Approve the request
    if response.action == "approve":
        friends[fr["from_id"]].append(fr["to_id"])
        friends[fr["to_id"]].append(fr["from_id"])
        fr["status"] = "approved"
        return {"message": "Friend request approved"}

    # Deny the request
    fr["status"] = "denied"
    return {"message": "Friend request denied"}

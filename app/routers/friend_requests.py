from fastapi import APIRouter

from app.schemas.friend_requests import (
    UserCreate,
    FriendRequestCreate,
    FriendRequestResponse,
)
from app.services.friend_requests import (
    create_user_service,
    send_friend_request_service,
    get_incoming_requests_service,
    respond_request_service,
)

router = APIRouter(tags=["Friend Requests"])


@router.post("/users", summary="Create a new user")
def create_user(user: UserCreate):
    return create_user_service(user)


@router.post("/friend-request", summary="Send a friend request")
def send_friend_request(req: FriendRequestCreate):
    return send_friend_request_service(req)


@router.get("/friend-request/{user_id}", summary="Get incoming friend requests")
def get_friend_requests(user_id: int):
    return get_incoming_requests_service(user_id)


@router.post("/friend-request/respond", summary="Respond to a friend request")
def respond_request(response: FriendRequestResponse):
    return respond_request_service(response)

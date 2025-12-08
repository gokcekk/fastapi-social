# app/routers/friend_request.py


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.friend_request import FriendRequest, RequestStatus
from app.schemas.friend_request import FriendRequestCreate, FriendRequestUpdate
from app.core.auth import get_current_user

router = APIRouter(prefix="/friend-request", tags=["Friend Requests"])


@router.post("", summary="Send a friend request")
def send_friend_request(
    req: FriendRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.id == req.to_user_id:
        raise HTTPException(status_code=400, detail="Cannot send a request to yourself")

    # Check if already friends
    if any(friend.id == req.to_user_id for friend in current_user.friends):
        raise HTTPException(status_code=400, detail="Already friends")

    # Create friend request
    friend_request = FriendRequest(
        from_user_id=current_user.id,
        to_user_id=req.to_user_id,
        status=RequestStatus.pending,
    )
    db.add(friend_request)
    db.commit()
    db.refresh(friend_request)

    return {"message": "Friend request sent", "request_id": friend_request.id}


@router.get("", summary="Get incoming friend requests")
def get_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    incoming = db.query(FriendRequest).filter_by(
        to_user_id=current_user.id,
        status=RequestStatus.pending
    ).all()

    return incoming


@router.post("/respond", summary="Approve or deny a request")
def respond_request(
    res: FriendRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    fr = db.query(FriendRequest).filter_by(
        id=res.request_id,
        to_user_id=current_user.id
    ).first()

    if not fr:
        raise HTTPException(status_code=404, detail="Request not found")

    if fr.status != RequestStatus.pending:
        raise HTTPException(status_code=400, detail="Already processed")

    if res.action == RequestStatus.approved:
        user1 = db.query(User).filter_by(id=fr.from_user_id).first()
        user2 = db.query(User).filter_by(id=fr.to_user_id).first()

        user1.friends.append(user2)
        user2.friends.append(user1)

    fr.status = res.action
    db.commit()

    return {"message": f"Friend request {res.action.value}"}

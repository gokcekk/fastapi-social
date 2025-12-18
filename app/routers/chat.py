from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.friend_request import FriendRequest, RequestStatus
from app.schemas.conversation import ConversationRead, ConversationStart

from app.core.security import SECRET_KEY, ALGORITHM
from app.db.database import SessionLocal
from app.models.conversation import Conversation
from app.models.message import Message


router = APIRouter(prefix="/chat", tags=["Chat"])

# chat_id -> active websocket connections
active_connections: Dict[int, List[WebSocket]] = {}

@router.post("/chats/start", response_model=ConversationRead)
def start_conversation(
    payload: ConversationStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or return a conversation using receiver_id."""
    if payload.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot start a chat with yourself.")

    receiver = db.get(User, payload.receiver_id)
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found.")

    if not _are_friends(db, current_user.id, payload.receiver_id):
        raise HTTPException(status_code=403, detail="Users are not friends.")

    return _get_or_create_conversation(db, current_user.id, payload.receiver_id)


def _are_friends(db: Session, a: int, b: int) -> bool:
    """Return True if users have an approved friendship."""
    return db.query(FriendRequest).filter(
        (
            (FriendRequest.from_user_id == a) & (FriendRequest.to_user_id == b)
        )
        | (
            (FriendRequest.from_user_id == b) & (FriendRequest.to_user_id == a)
        ),
        FriendRequest.status == RequestStatus.approved,
    ).first() is not None


def _get_or_create_conversation(db: Session, a: int, b: int) -> Conversation:
    """Find an existing conversation between two users or create a new one."""
    convo = db.query(Conversation).filter(
        (
            (Conversation.user1_id == a) & (Conversation.user2_id == b)
        )
        | (
            (Conversation.user1_id == b) & (Conversation.user2_id == a)
        )
    ).first()

    if convo:
        return convo

    convo = Conversation(user1_id=a, user2_id=b)
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return convo



def _decode_user_id(token: str) -> int:
    """Decode JWT and return the user id from the 'sub' claim."""
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return int(payload.get("sub"))


def _open_db_session() -> Session:
    """Create a new database session for WebSocket handlers."""
    return SessionLocal()


def _is_participant(convo: Conversation, user_id: int) -> bool:
    """Check if the user is a participant of the conversation."""
    return user_id in (convo.user1_id, convo.user2_id)


@router.websocket("/ws/{chat_id}")
async def websocket_chat(websocket: WebSocket, chat_id: int):
    """
    WebSocket endpoint for real-time chat.

    - Auth: ?token=<JWT>
    - Authorization: only conversation participants can connect
    - Persistence: incoming messages are saved to the database
    - Broadcast: messages are sent to other clients connected to the same chat
    """
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)  # Policy violation
        return

    try:
        user_id = _decode_user_id(token)
    except (JWTError, ValueError, TypeError):
        await websocket.close(code=1008)
        return

    db = _open_db_session()
    try:
        convo = db.get(Conversation, chat_id)
        if not convo or not _is_participant(convo, user_id):
            await websocket.close(code=1008)
            return

        await websocket.accept()
        active_connections.setdefault(chat_id, []).append(websocket)

        try:
            while True:
                content = await websocket.receive_text()

                message = Message(
                    conversation_id=chat_id,
                    sender_id=user_id,
                    content=content,
                )
                db.add(message)
                db.commit()

                for conn in active_connections.get(chat_id, []):
                    if conn is not websocket:
                        await conn.send_text(f"{user_id}: {content}")

        except WebSocketDisconnect:
            pass
        finally:
            if websocket in active_connections.get(chat_id, []):
                active_connections[chat_id].remove(websocket)

    finally:
        db.close()

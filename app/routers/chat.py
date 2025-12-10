from typing import Dict, List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.friend_request import FriendRequest, RequestStatus
from app.models.user import User
from app.schemas.conversation import ConversationRead
from app.schemas.message import (
    MessageRead,
    MessageCreate,
    DirectMessageCreate,
)

router = APIRouter(prefix="/chat", tags=["Chat"])


# conversation_id -> aktif websocket bağlantıları
active_connections: Dict[int, List[WebSocket]] = {}


def are_friends(db: Session, a: int, b: int) -> bool:
    """
    Kullanıcıların arkadaş olup olmadığını kontrol eder.
    """
    return db.query(FriendRequest).filter(
        (
            (FriendRequest.from_user_id == a)
            & (FriendRequest.to_user_id == b)
        )
        | (
            (FriendRequest.from_user_id == b)
            & (FriendRequest.to_user_id == a)
        ),
        FriendRequest.status == RequestStatus.approved,
    ).first() is not None


@router.get("/chats", response_model=list[ConversationRead])
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Kullanıcının bulunduğu tüm sohbetleri getirir.
    """
    return db.query(Conversation).filter(
        (Conversation.user1_id == current_user.id)
        | (Conversation.user2_id == current_user.id)
    ).all()


@router.get("/chats/{chat_id}/messages", response_model=list[MessageRead])
def get_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bir sohbetin mesaj geçmişini getirir.
    """
    convo = db.get(Conversation, chat_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if current_user.id not in [convo.user1_id, convo.user2_id]:
        raise HTTPException(status_code=403, detail="Not your conversation")

    return convo.messages


@router.post("/chats/{chat_id}/messages", response_model=MessageRead)
def send_message_in_chat(
    chat_id: int,
    msg: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Var olan bir chat_id üzerinden mesaj gönderir.
    """
    convo = db.get(Conversation, chat_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if current_user.id not in [convo.user1_id, convo.user2_id]:
        raise HTTPException(status_code=403, detail="Not your conversation")

    message = Message(
        conversation_id=chat_id,
        sender_id=current_user.id,
        content=msg.content,
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    return message


@router.post("/send", response_model=MessageRead)
def send_direct_message(
    msg: DirectMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    receiver_id vererek direkt mesaj gönder.
    Eğer böyle bir sohbet yoksa otomatik oluştur.
    """

    # Arkadaş kontrolü
    if not are_friends(db, current_user.id, msg.receiver_id):
        raise HTTPException(status_code=403, detail="Users are not friends.")

    # Mevcut conversation var mı?
    convo = db.query(Conversation).filter(
        (
            (Conversation.user1_id == current_user.id)
            & (Conversation.user2_id == msg.receiver_id)
        )
        | (
            (Conversation.user1_id == msg.receiver_id)
            & (Conversation.user2_id == current_user.id)
        )
    ).first()

    if not convo:
        convo = Conversation(
            user1_id=current_user.id,
            user2_id=msg.receiver_id
        )
        db.add(convo)
        db.commit()
        db.refresh(convo)

    message = Message(
        conversation_id=convo.id,
        sender_id=current_user.id,
        content=msg.content
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    return message


@router.websocket("/ws/{chat_id}")
async def websocket_chat(websocket: WebSocket, chat_id: int):
    """
    WebSocket: Gerçek zamanlı mesajlaşma için kullanılacak.
    Şu an sadece echo.
    """
    await websocket.accept()
    active_connections.setdefault(chat_id, []).append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        active_connections[chat_id].remove(websocket)

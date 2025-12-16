from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.conversation import Conversation
from app.models.message import Message

# ✅ Router MUST be defined before usage
router = APIRouter(prefix="/chat", tags=["Chat"])

# Active WebSocket connections per conversation.
active_connections: Dict[int, List[WebSocket]] = {}


def get_db_session() -> Session:
    return SessionLocal()


@router.websocket("/ws/{chat_id}")
async def websocket_chat(websocket: WebSocket, chat_id: int):
    # 🔹 Token al
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    # 🔹 Token decode
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sender_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        await websocket.close(code=1008)
        return

    # 🔹 DB session (MANUEL)
    db = get_db_session()

    # 🔹 Conversation control
    convo = db.get(Conversation, chat_id)
    if not convo or sender_id not in [convo.user1_id, convo.user2_id]:
        db.close()
        await websocket.close(code=1008)
        return

    # 🔹 ACCEPT EN BAŞTA
    await websocket.accept()
    active_connections.setdefault(chat_id, []).append(websocket)

    try:
        while True:
            content = await websocket.receive_text()

            # 🔹 Mesajı DB’ye kaydet
            message = Message(
                conversation_id=chat_id,
                sender_id=sender_id,
                content=content,
            )
            db.add(message)
            db.commit()

            # 🔹 Diğer clientlara gönder
            for conn in active_connections.get(chat_id, []):
                if conn != websocket:
                    await conn.send_text(
                        f"{sender_id}: {content}"
                    )

    except WebSocketDisconnect:
        active_connections[chat_id].remove(websocket)
        db.close()

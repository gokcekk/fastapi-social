from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.security import SECRET_KEY, ALGORITHM
from app.db.database import SessionLocal
from app.models.conversation import Conversation
from app.models.message import Message

router = APIRouter(prefix="/chat", tags=["Chat"])

# chat_id -> active websocket connections
active_connections: Dict[int, List[WebSocket]] = {}


def _decode_sender_id(token: str) -> int:
    """Decode JWT and return sender user_id from 'sub'."""
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    sub = payload.get("sub")
    return int(sub)


def _get_db() -> Session:
    """Create a DB session for WebSocket usage."""
    return SessionLocal()


@router.websocket("/ws/{chat_id}")
async def websocket_chat(websocket: WebSocket, chat_id: int):
    """
    WebSocket endpoint for realtime chat.
    - Auth via ?token=JWT
    - Saves messages to DB
    - Broadcasts messages to other clients in the same chat
    """
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)  # Policy violation
        return

    try:
        sender_id = _decode_sender_id(token)
    except (JWTError, ValueError, TypeError):
        await websocket.close(code=1008)
        return

    db = _get_db()

    try:
        convo = db.get(Conversation, chat_id)
        if not convo or sender_id not in (convo.user1_id, convo.user2_id):
            await websocket.close(code=1008)
            return

        await websocket.accept()
        active_connections.setdefault(chat_id, []).append(websocket)

        try:
            while True:
                content = await websocket.receive_text()

                # Persist message
                message = Message(
                    conversation_id=chat_id,
                    sender_id=sender_id,
                    content=content,
                )
                db.add(message)
                db.commit()

                # Broadcast to other clients (same chat)
                for conn in active_connections.get(chat_id, []):
                    if conn is not websocket:
                        await conn.send_text(f"{sender_id}: {content}")

        except WebSocketDisconnect:
            # Client disconnected
            pass
        finally:
            if chat_id in active_connections and websocket in active_connections[chat_id]:
                active_connections[chat_id].remove(websocket)

    finally:
        db.close()

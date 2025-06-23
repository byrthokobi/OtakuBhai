from fastapi import APIRouter, Depends, HTTPException
from app.auth.jwt_bearer import JWTBearer
from app.models.chat_history import ChatCreate, ChatInDB, Message
from app.llm.llm_handler import get_llm_response
from app.db.mongo import conversations_collection
from bson import ObjectId
from typing import List
import datetime

chat_router = APIRouter(prefix="/chat", tags=["Chat"])

# POST /chat
@chat_router.post("/", dependencies=[Depends(JWTBearer())])
def start_chat(chat: ChatCreate, payload: dict = Depends(JWTBearer())):
    user_email = payload.get("sub")
    user_msg = chat.user_message
    bot_reply = get_llm_response(user_msg)

    chat_doc = ChatInDB(
        user_email=user_email,
        title=user_msg[:50],  # Simple title based on user prompt
        messages=[
            Message(sender="user", text=user_msg),
            Message(sender="bot", text=bot_reply)
        ]
    )

    inserted = conversations_collection.insert_one(chat_doc.dict())
    return {"chat_id": str(inserted.inserted_id), "bot_reply": bot_reply}

# GET /chat
@chat_router.get("/", dependencies=[Depends(JWTBearer())])
def get_user_chats(payload: dict = Depends(JWTBearer())):
    user_email = payload.get("sub")
    chats = conversations_collection.find({"user_email": user_email})
    return [
        {"chat_id": str(chat["_id"]), "title": chat["title"], "created_at": chat["created_at"]}
        for chat in chats
    ]

# GET /chat/{id}
@chat_router.get("/{chat_id}", dependencies=[Depends(JWTBearer())])
def get_single_chat(chat_id: str, payload: dict = Depends(JWTBearer())):
    chat = conversations_collection.find_one({"_id": ObjectId(chat_id)})
    if not chat or chat["user_email"] != payload.get("sub"):
        raise HTTPException(status_code=404, detail="Chat not found")
    chat["_id"] = str(chat["_id"])
    return chat

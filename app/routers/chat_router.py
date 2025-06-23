from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import StreamingResponse

from app.auth.jwt_bearer import JWTBearer
from app.models.chat_history import ChatCreate, ChatInDB, Message
from app.llm.llm_handler import get_llm_response, stream_llm_response
from app.db.mongo import conversations_collection
from bson import ObjectId

chat_router = APIRouter(prefix="/chat", tags=["Chat"])

# POST /chat
@chat_router.post("/", dependencies=[Depends(JWTBearer())])
async def start_chat(chat: ChatCreate, payload: dict = Depends(JWTBearer())):
    user_email = payload.get("sub")
    user_msg = chat.user_message
    bot_reply = await get_llm_response(user_msg)

    chat_doc = ChatInDB(
        user_email=user_email,
        title=user_msg[:50],
        messages=[
            Message(sender="user", text=user_msg),
            Message(sender="bot", text=bot_reply)
        ]
    )

    inserted = conversations_collection.insert_one(chat_doc.dict())
    return {"chat_id": str(inserted.inserted_id), "bot_reply": bot_reply}

# GET /chat
@chat_router.get("/", dependencies=[Depends(JWTBearer())])
def get_user_chats(payload: dict = Depends(JWTBearer()), skip: int = 0, limit: int = 10):
    user_email = payload.get("sub")
    chats_cursor = conversations_collection.find({"user_email": user_email}).sort("created_at", -1).skip(skip).limit(limit)
    return [
        {"chat_id": str(chat["_id"]), "title": chat["title"], "created_at": chat["created_at"]}
        for chat in chats_cursor
    ]

# GET /chat/{id}
@chat_router.get("/{chat_id}", dependencies=[Depends(JWTBearer())])
def get_single_chat(chat_id: str, payload: dict = Depends(JWTBearer())):
    chat = conversations_collection.find_one({"_id": ObjectId(chat_id)})
    if not chat or chat["user_email"] != payload.get("sub"):
        raise HTTPException(status_code=404, detail="Chat not found")
    chat["_id"] = str(chat["_id"])
    return chat

@chat_router.post("/stream", response_class=StreamingResponse, dependencies=[Depends(JWTBearer())])
async def stream_chat(chat: ChatCreate, payload: dict = Depends(JWTBearer())):
    return await stream_llm_response(chat.user_message)

@chat_router.post("/{chat_id}/continue", dependencies=[Depends(JWTBearer())])
async def continue_chat(chat_id: str, chat: ChatCreate, payload: dict = Depends(JWTBearer())):
    user_email = payload.get("sub")
    existing = conversations_collection.find_one({"_id": ObjectId(chat_id)})

    if not existing or existing["user_email"] != user_email:
        raise HTTPException(status_code=404, detail="Conversation not found")

    user_msg = chat.user_message
    bot_reply = await get_llm_response(user_msg)

    new_messages = [
        Message(sender="user", text=user_msg),
        Message(sender="bot", text=bot_reply)
    ]

    conversations_collection.update_one(
        {"_id": ObjectId(chat_id)},
        {"$push": {"messages": {"$each": [m.dict() for m in new_messages]}}}
    )

    return {"bot_reply": bot_reply}

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    sender: str  # 'user' or 'bot'
    text: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

class ChatCreate(BaseModel):
    user_message: str

class ChatInDB(BaseModel):
    user_email: str
    title: str
    messages: List[Message]
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
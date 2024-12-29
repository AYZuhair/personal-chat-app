# backend/models/chat.py
from pydantic import BaseModel
from typing import List

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class ChatHistory(BaseModel):
    messages: List[ChatMessage]
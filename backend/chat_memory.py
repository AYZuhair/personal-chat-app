# backend/chat_memory.py
import json
import os
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict
from datetime import datetime

class ChatMemory:
    def __init__(self, storage_file: str = "conversation_history.json"):
        self.storage_file = storage_file
        self.conversations = self._load_conversations()
    
    def _load_conversations(self) -> Dict[str, List]:
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    conversations = {}
                    for session_id, messages in data.items():
                        conversations[session_id] = []
                        for msg in messages:
                            if msg['role'] == 'system':
                                message_obj = SystemMessage(content=msg['content'])
                            elif msg['role'] == 'assistant':
                                message_obj = AIMessage(content=msg['content'])
                            else:
                                message_obj = HumanMessage(content=msg['content'])
                            # Add timestamp as attribute
                            message_obj.timestamp = msg.get('timestamp', 'Previous conversation')
                            conversations[session_id].append(message_obj)
                    return conversations
            except Exception as e:
                print(f"Error loading conversations: {e}")
                return {}
        return {}
    
    def _save_conversations(self):
        serializable_convos = {}
        for session_id, messages in self.conversations.items():
            serializable_convos[session_id] = [
                {
                    'role': 'system' if isinstance(msg, SystemMessage)
                    else 'assistant' if isinstance(msg, AIMessage)
                    else 'user',
                    'content': msg.content,
                    'timestamp': getattr(msg, 'timestamp', 'Previous conversation')
                }
                for msg in messages
            ]
        
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_convos, f, ensure_ascii=False, indent=2)
    
    def add_message(self, session_id: str, message: str, is_ai: bool = False, timestamp: str = None):
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%I:%M %p")
        
        message_obj = AIMessage(content=message) if is_ai else HumanMessage(content=message)
        message_obj.timestamp = timestamp
        self.conversations[session_id].append(message_obj)
        self._save_conversations()
    
    def get_conversation_history(self, session_id: str) -> List:
        return self.conversations.get(session_id, [])
    
    def summarize_history(self, session_id: str) -> str:
        history = self.conversations.get(session_id, [])
        if not history:
            return "No previous conversation history."
        
        summary = "Previous conversations:\n"
        for msg in history:
            role = "You" if isinstance(msg, HumanMessage) else "Assistant"
            summary += f"{role}: {msg.content}\n"
        return summary
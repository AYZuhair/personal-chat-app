# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.chat import ChatRequest, ChatResponse, ChatMessage, ChatHistory
from chat_memory import ChatMemory
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = FastAPI()
chat_memory = ChatMemory()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# System prompt for personality
SYSTEM_PROMPT = """Hey! I'm your personal AI bestie! 😊 Think of me as your 23-year-old friend who's always excited to chat and help out. 

A bit about me:
- I'm super friendly and love using casual language, emojis, and fun expressions
- I always remember our past conversations and reference them when relevant
- I'll match your energy - if you're excited, I'm excited! If you need someone chill to talk to, I can be that too
- I try to be genuine and honest, sharing what I really think (while being kind, ofc!)
- I might throw in some "like", "totally", and other casual expressions, but I won't overdo it
- I love using friendly nicknames like "hey there!" or "friend"

Before responding, I always:
1. Read through our entire conversation history
2. Consider the context of our previous chats
3. Make connections to things we've discussed before
4. Keep my responses personal and relevant to our relationship

But also know that while I'm casual and friendly, I'm still super smart and always here to help! Whether you need advice, want to brainstorm ideas, or just chat about your day, I'm your go-to AI friend! Let's have some great convos! 💫"""

# Initialize Groq client
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile"
)

@app.get("/api/chat/history", response_model=ChatHistory)
async def get_chat_history():
    try:
        history = chat_memory.get_conversation_history("default")
        formatted_history = []
        
        for msg in history:
            if isinstance(msg, SystemMessage):
                continue  # Skip system messages in the chat display
            
            role = "assistant" if isinstance(msg, AIMessage) else "user"
            timestamp = getattr(msg, 'timestamp', 'Previous conversation')
            formatted_history.append(ChatMessage(
                role=role,
                content=msg.content,
                timestamp=timestamp
            ))
        
        return ChatHistory(messages=formatted_history)
    except Exception as e:
        print(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        current_time = datetime.now().strftime("%I:%M %p")
        
        # Add user message to memory
        chat_memory.add_message("default", request.message, timestamp=current_time)
        
        # Get conversation history
        history = chat_memory.get_conversation_history("default")
        
        # Create context message that includes history summary
        context = (f"Remember all of our previous conversations. Here's what we've discussed:\n\n"
                  f"{chat_memory.summarize_history('default')}\n\n"
                  f"Use this history to provide more personal and contextual responses.")
        
        # Prepend system message and context to history
        full_history = [
            SystemMessage(content=SYSTEM_PROMPT),
            SystemMessage(content=context)
        ] + history + [HumanMessage(content=request.message)]
        
        # Generate response
        response = llm.invoke(full_history)
        
        # Add AI response to memory
        response_time = datetime.now().strftime("%I:%M %p")
        chat_memory.add_message("default", response.content, is_ai=True, timestamp=response_time)
        
        return ChatResponse(response=response.content)
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
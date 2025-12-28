import uuid
from typing import Dict, List, Tuple
from datetime import datetime
from rag.chatbot import rag_chatbot
from rag.retriever import retrieve_chunks
from backend.config import RAG_TOP_K, MAX_CHAT_HISTORY


class ChatMemory:
    """In-memory chat session storage"""
    
    def __init__(self):
        self.sessions: Dict[str, List[Dict]] = {}
    
    def create_session(self) -> str:
        """Generate new chat session ID"""
        chat_id = f"chat_{uuid.uuid4().hex[:12]}"
        self.sessions[chat_id] = []
        return chat_id
    
    def add_message(self, chat_id: str, role: str, content: str):
        """Add message to chat history"""
        if chat_id not in self.sessions:
            self.sessions[chat_id] = []
        
        self.sessions[chat_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent messages
        if len(self.sessions[chat_id]) > MAX_CHAT_HISTORY * 2:
            self.sessions[chat_id] = self.sessions[chat_id][-MAX_CHAT_HISTORY * 2:]
    
    def get_history(self, chat_id: str) -> List[Dict]:
        """Get chat history"""
        return self.sessions.get(chat_id, [])
    
    def delete_session(self, chat_id: str):
        """Delete chat session"""
        if chat_id in self.sessions:
            del self.sessions[chat_id]


# Global chat memory instance
chat_memory = ChatMemory()


def process_chat_request(message: str, chat_id: str = None) -> Tuple[str, str, List[Dict]]:
    """
    Process chat request and return response with sources
    
    Returns:
        Tuple of (chat_id, response_message, sources)
    """
    # Create or use existing session
    if not chat_id:
        chat_id = chat_memory.create_session()
    elif chat_id not in chat_memory.sessions:
        chat_memory.sessions[chat_id] = []
    
    # Store user message
    chat_memory.add_message(chat_id, "user", message)
    
    # Get RAG response
    response = rag_chatbot(message, k=RAG_TOP_K)
    
    # Store assistant response
    chat_memory.add_message(chat_id, "assistant", response)
    
    # Get sources
    sources = retrieve_chunks(message, k=3)
    
    # Format sources
    formatted_sources = []
    for source in sources:
        formatted_sources.append({
            "text": source.get("text", "")[:200],
            "score": source.get("score", 0.0),
            "url": source.get("url"),
            "title": source.get("title")
        })
    
    return chat_id, response, formatted_sources


def get_chat_history(chat_id: str) -> List[Dict]:
    """Get chat history for a session"""
    return chat_memory.get_history(chat_id)

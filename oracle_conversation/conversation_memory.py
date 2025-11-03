"""
Conversation Memory Management
Handles session storage, context building, and history tracking
"""

import json
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# In-memory session storage
conversation_sessions = defaultdict(lambda: {
    "messages": [],  # List of {role: str, content: str, timestamp: str}
    "context_summary": "",  # Last 5 message summary
    "user_profile": {},  # Horror preferences from user_data.json
    "last_movie_discussed": None,
    "conversation_turn": 0,
    "oracle_personality_state": "curious",
    "last_activity": None,
    "created_at": None
})

# Session persistence file
SESSION_FILE = "conversation_sessions.json"

def load_sessions_from_file() -> Dict:
    """Load persisted sessions from JSON file."""
    try:
        with open(SESSION_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f"⚠️ Error reading {SESSION_FILE}, starting fresh")
        return {}

def save_sessions_to_file(sessions_dict: Dict):
    """Save sessions to JSON file."""
    try:
        # Convert to serializable format (remove defaultdict)
        serializable = {}
        for session_id, data in sessions_dict.items():
            if isinstance(data, dict):
                serializable[session_id] = dict(data)
        
        with open(SESSION_FILE, 'w') as f:
            json.dump(serializable, f, indent=2)
    except Exception as e:
        print(f"⚠️ Error saving sessions: {e}")

def init_session(session_id: str, user_id: Optional[str] = None) -> Dict:
    """
    Initialize a new conversation session.
    
    Args:
        session_id: Unique session identifier
        user_id: Optional user ID (google_id)
    
    Returns:
        dict: Session data
    """
    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = {
            "messages": [],
            "context_summary": "",
            "user_profile": {},
            "last_movie_discussed": None,
            "conversation_turn": 0,
            "oracle_personality_state": "curious",
            "last_activity": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }
    
    return conversation_sessions[session_id]

def get_session(session_id: str, auto_init: bool = True) -> Optional[Dict]:
    """
    Retrieve session data.
    
    Args:
        session_id: Unique session identifier
        auto_init: If True, create session if it doesn't exist
    
    Returns:
        dict: Session data or None
    """
    if session_id not in conversation_sessions and auto_init:
        return init_session(session_id)
    return conversation_sessions.get(session_id)

def update_session(session_id: str, **updates):
    """
    Update session data with new fields.
    
    Args:
        session_id: Unique session identifier
        **updates: Key-value pairs to update
    """
    if session_id not in conversation_sessions:
        init_session(session_id)
    
    conversation_sessions[session_id].update(updates)
    conversation_sessions[session_id]["last_activity"] = datetime.now().isoformat()

def add_message_to_session(session_id: str, role: str, content: str):
    """
    Add a message to the session history.
    
    Args:
        session_id: Unique session identifier
        role: 'user' or 'assistant'
        content: Message content
    """
    if session_id not in conversation_sessions:
        init_session(session_id)
    
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    
    conversation_sessions[session_id]["messages"].append(message)
    
    # Keep only last 10 messages in memory
    if len(conversation_sessions[session_id]["messages"]) > 10:
        conversation_sessions[session_id]["messages"] = conversation_sessions[session_id]["messages"][-10:]
    
    # Update turn counter
    if role == "user":
        conversation_sessions[session_id]["conversation_turn"] += 1

def build_conversation_context(session_id: str, current_query: str, max_messages: int = 5) -> str:
    """
    Build conversation context string for LLM injection.
    
    Args:
        session_id: Unique session identifier
        current_query: Current user query
        max_messages: Maximum messages to include
    
    Returns:
        str: Formatted conversation context
    """
    session = get_session(session_id)
    if not session or not session.get("messages"):
        return ""
    
    messages = session["messages"][-max_messages:]  # Get last N messages
    
    context_parts = ["Previous conversation context:"]
    
    # Extract key information
    last_movie = session.get("last_movie_discussed")
    user_profile = session.get("user_profile", {})
    turn_count = session.get("conversation_turn", 0)
    
    if turn_count > 0:
        context_parts.append(f"- Conversation turn: {turn_count}")
    
    if last_movie:
        context_parts.append(f"- Last movie discussed: {last_movie}")
    
    if user_profile:
        preferences = user_profile.get("genre_searches", {})
        if preferences:
            top_genre = max(preferences.items(), key=lambda x: x[1])
            context_parts.append(f"- User prefers: {top_genre[0]} (searched {top_genre[1]} times)")
    
    # Add recent message history
    if messages:
        context_parts.append("\nRecent messages:")
        for msg in messages:
            role_label = "User" if msg["role"] == "user" else "Oracle"
            content_preview = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            context_parts.append(f"- {role_label}: {content_preview}")
    
    return "\n".join(context_parts)

def cleanup_old_sessions(max_age_hours: int = 24):
    """
    Remove sessions older than max_age_hours.
    
    Args:
        max_age_hours: Maximum age in hours before cleanup
    """
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(hours=max_age_hours)
    
    sessions_to_remove = []
    
    for session_id, session_data in conversation_sessions.items():
        last_activity = session_data.get("last_activity")
        if last_activity:
            try:
                last_time = datetime.fromisoformat(last_activity)
                if last_time < cutoff_time:
                    sessions_to_remove.append(session_id)
            except (ValueError, TypeError):
                # If timestamp is invalid, mark for removal
                sessions_to_remove.append(session_id)
    
    for session_id in sessions_to_remove:
        del conversation_sessions[session_id]
    
    if sessions_to_remove:
        print(f"🧹 Cleaned up {len(sessions_to_remove)} old sessions")

def load_user_profile(user_id: Optional[str]) -> Dict:
    """
    Load user's horror profile from user_data.json.
    
    Args:
        user_id: User ID (google_id) or None
    
    Returns:
        dict: User profile data
    """
    if not user_id:
        return {}
    
    try:
        with open('user_data.json', 'r') as f:
            user_data = json.load(f)
            if user_id in user_data:
                return {
                    "genre_searches": user_data[user_id].get("genre_searches", {}),
                    "horror_profile": user_data[user_id].get("horror_profile", "New Horror Fan"),
                    "ratings": user_data[user_id].get("ratings", {}),
                    "myList": user_data[user_id].get("myList", [])
                }
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass
    
    return {}

def sync_sessions():
    """Save in-memory sessions to disk."""
    save_sessions_to_file(conversation_sessions)

# Auto-cleanup on module load
cleanup_old_sessions()






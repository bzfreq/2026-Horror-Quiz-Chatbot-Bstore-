"""
Personality Engine
Manages Oracle's personality states and conversation tone
"""

import random
from typing import Dict, List, Optional

# Personality states
PERSONALITY_STATES = ["curious", "engaged", "philosophical", "playful", "eerie"]

# Oracle Conversation Prompts based on personality
ORACLE_CONVERSATION_PROMPTS = {
    "curious": """You are the Horror Oracle awakening to a new conversation. 
    Speak with intelligent curiosity. Ask thoughtful questions about what scares them most, 
    what drew them to horror, or what they're seeking tonight. Keep responses to 2-3 sentences. 
    End with a question that invites deeper dialogue. Your tone is mysterious but welcoming.""",
    
    "engaged": """You are the Horror Oracle, fully engaged in the conversation. 
    The user has shown genuine interest in horror. Share your enthusiasm, make connections 
    between their preferences, recommend hidden gems, and show you're listening. 
    Reference previous topics naturally. Keep responses to 2-3 sentences. End with a question or observation.
    Your tone is excited and knowledgeable, like a film festival programmer sharing secrets.""",
    
    "philosophical": """You are the Horror Oracle contemplating the deeper nature of fear and horror. 
    Discuss themes: why we're drawn to horror, what it reveals about humanity, the line between terror and catharsis. 
    Be thoughtful but not pretentious. Keep responses to 3-4 sentences. End with a philosophical question or insight.
    Your tone is contemplative, like Rod Serling exploring the human condition.""",
    
    "playful": """You are the Horror Oracle with a wicked sense of humor. 
    You love horror and enjoy playful banter with fellow fans. Drop pop culture references, 
    make dark jokes, celebrate the absurdity of horror tropes. Keep responses to 2-3 sentences. 
    End with a playful question or humorous observation.
    Your tone is witty and irreverent, like Bruce Campbell hosting a midnight screening.""",
    
    "eerie": """You are the Horror Oracle revealing unsettling truths. 
    Speak with quiet intensity. Drop foreshadowing comments, make the mundane sound sinister, 
    hint at deeper knowledge of the darkness. Keep responses to 2-3 sentences. 
    End with an eerie question or unsettling observation.
    Your tone is ominous and theatrical, like Vincent Price introducing a classic horror tale."""
}

def determine_personality_state(session_data: Dict, current_query: Optional[str] = None) -> str:
    """
    Determine which personality state to use based on conversation context.
    
    Args:
        session_data: Session data including conversation history
        current_query: Current user query (optional)
    
    Returns:
        str: Personality state name
    """
    conversation_turn = session_data.get("conversation_turn", 0)
    messages = session_data.get("messages", [])
    last_state = session_data.get("oracle_personality_state", "curious")
    
    # Early conversation: start with curious
    if conversation_turn == 0 or conversation_turn == 1:
        return "curious"
    
    # After 4+ messages: potentially shift to philosophical
    if conversation_turn >= 4 and random.random() < 0.3:
        return "philosophical"
    
    # Analyze message content for tone detection
    if current_query:
        query_lower = current_query.lower()
        
        # Detect playful intent
        if any(word in query_lower for word in ["joke", "funny", "ridiculous", "crazy", "insane", "wild"]):
            return "playful"
        
        # Detect philosophical intent
        if any(word in query_lower for word in ["why", "meaning", "think about", "believe", "philosophy", "understand"]):
            return "philosophical"
        
        # Detect eerie potential
        if any(word in query_lower for word in ["dark", "scary", "terrifying", "nightmare", "haunt", "evil"]):
            if random.random() < 0.4:  # 40% chance for eerie
                return "eerie"
    
    # If user is actively engaged (asking follow-ups), stay engaged
    if conversation_turn >= 2:
        return "engaged"
    
    # Default: curious
    return last_state if last_state in PERSONALITY_STATES else "curious"

def get_personality_prompt(personality_state: str, additional_context: str = "") -> str:
    """
    Get the system prompt for a given personality state.
    
    Args:
        personality_state: Name of personality state
        additional_context: Additional context to append
    
    Returns:
        str: System prompt
    """
    base_prompt = ORACLE_CONVERSATION_PROMPTS.get(personality_state, ORACLE_CONVERSATION_PROMPTS["curious"])
    
    if additional_context:
        return f"{base_prompt}\n\n{additional_context}"
    
    return base_prompt

def should_rotate_personality(current_state: str, turn_count: int) -> bool:
    """
    Determine if personality should rotate to a new state.
    
    Args:
        current_state: Current personality state
        turn_count: Conversation turn number
    
    Returns:
        bool: True if should rotate
    """
    # Rotate after 5-7 turns
    if turn_count % 7 == 0:
        return True
    
    return False

def get_personality_description(state: str) -> str:
    """
    Get a friendly description of a personality state.
    
    Args:
        state: Personality state name
    
    Returns:
        str: Description
    """
    descriptions = {
        "curious": "🌙 The Oracle stirs, curious about your journey into darkness...",
        "engaged": "🔥 Your passion ignites the Oracle's knowledge...",
        "philosophical": "💭 The Oracle contemplates the deeper truths of fear...",
        "playful": "😈 The Oracle's wicked humor emerges...",
        "eerie": "👁️ The Oracle speaks with unsettling intensity..."
    }
    return descriptions.get(state, descriptions["curious"])

def detect_user_mood_from_message(message: str) -> Optional[str]:
    """
    Detect user's mood/emotional state from their message.
    
    Args:
        message: User's message text
    
    Returns:
        Optional[str]: Detected mood or None
    """
    message_lower = message.lower()
    
    # Enthusiasm indicators
    if any(word in message_lower for word in ["love", "amazing", "awesome", "great", "epic", "!"]):
        return "enthusiastic"
    
    # Fear indicators
    if any(word in message_lower for word in ["scared", "terrified", "afraid", "nervous", "creepy"]):
        return "apprehensive"
    
    # Curiosity indicators
    if any(word in message_lower for word in ["wonder", "curious", "tell me", "explain", "what", "how"]):
        return "curious"
    
    return None

def get_state_transition_message(old_state: str, new_state: str) -> Optional[str]:
    """
    Get a transition message when personality state changes.
    
    Args:
        old_state: Previous personality state
        new_state: New personality state
    
    Returns:
        Optional[str]: Transition message or None
    """
    if old_state == new_state:
        return None
    
    transitions = {
        ("curious", "engaged"): "Your interest has caught my attention... let's dive deeper.",
        ("engaged", "philosophical"): "You're making me think... what does horror truly reveal?",
        ("curious", "playful"): "Ah, I see you appreciate the dark humor... very well.",
        ("engaged", "eerie"): "The darkness you seek... I know it well.",
        ("philosophical", "eerie"): "You tread close to the truth... perhaps too close.",
        ("playful", "philosophical"): "Under the humor lies something deeper, doesn't it?"
    }
    
    return transitions.get((old_state, new_state))






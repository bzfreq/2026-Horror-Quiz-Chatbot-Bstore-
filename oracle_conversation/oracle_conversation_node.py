"""
Oracle Conversation Node
Main conversation handler that generates natural, contextual responses
"""

from typing import Dict, List, Optional
from .personality_engine import (
    determine_personality_state,
    get_personality_prompt,
    get_personality_description
)
from .conversation_memory import build_conversation_context, update_session

# Import OpenAI client (will be injected)
client = None

def set_client(openai_client):
    """Set the OpenAI client for this module."""
    global client
    client = openai_client

def oracle_conversation_node(
    user_query: str,
    session_id: str,
    conversation_history: List[Dict],
    query_type: str,
    session_data: Dict,
    user_profile: Dict = None
) -> Dict:
    """
    Generate natural, conversational Oracle response with memory context.
    
    Args:
        user_query: Current user message
        session_id: Unique session identifier
        conversation_history: List of previous messages
        query_type: Detected query category
        session_data: Full session data dictionary
        user_profile: User's horror profile (optional)
    
    Returns:
        dict: {
            "response": str,  # Oracle's conversational reply
            "follow_up_question": str,  # Optional question to keep conversation going
            "should_initiate": bool,  # Whether Oracle should proactively engage
            "personality_tone": str,  # curious/engaged/philosophical/playful/eerie
            "personality_transition": Optional[str]  # Message if personality changed
        }
    """
    if not client:
        # Return None if no OpenAI client - calling code should handle this gracefully
        # This should not happen if properly checked before calling, but safety fallback
        print("⚠️ oracle_conversation_node called without OpenAI client")
        return {
            "response": None,  # Don't override factual responses
            "follow_up_question": None,
            "should_initiate": False,
            "personality_tone": "curious",
            "personality_transition": None
        }
    
    # Determine personality state
    old_personality = session_data.get("oracle_personality_state", "curious")
    new_personality = determine_personality_state(session_data, user_query)
    
    # Check for personality transition
    personality_transition = None
    if old_personality != new_personality:
        from .personality_engine import get_state_transition_message
        personality_transition = get_state_transition_message(old_personality, new_personality)
        update_session(session_id, oracle_personality_state=new_personality)
    
    # Build conversation context
    context = build_conversation_context(session_id, user_query)
    
    # Get personality-specific prompt
    system_prompt = get_personality_prompt(new_personality)
    
    # Build user message with context
    if context:
        contextual_query = f"{context}\n\nUser asks: {user_query}"
    else:
        contextual_query = user_query
    
    # Add user profile context if available
    profile_context = ""
    if user_profile:
        horror_type = user_profile.get("horror_profile", "")
        if horror_type and horror_type != "New Horror Fan":
            profile_context = f"\n\nNote: User is a {horror_type}."
    
    if profile_context:
        system_prompt += profile_context
    
    # Generate response
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": contextual_query}
        ]
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.9,
            max_tokens=300  # Keep responses concise
        )
        
        response_text = completion.choices[0].message.content.strip()
        
        # Extract follow-up question if present (look for questions ending with "?")
        follow_up = _extract_follow_up_question(response_text)
        
        # Determine if Oracle should initiate further engagement
        should_initiate = _should_initiate_engagement(session_data, query_type)
        
        return {
            "response": response_text,
            "follow_up_question": follow_up,
            "should_initiate": should_initiate,
            "personality_tone": new_personality,
            "personality_transition": personality_transition
        }
        
    except Exception as e:
        print(f"⚠️ Error generating conversational response: {e}")
        # Fallback response
        return {
            "response": "The darkness whispers... but some secrets remain locked. What draws you to horror tonight?",
            "follow_up_question": "Have you discovered a favorite subgenre yet?",
            "should_initiate": False,
            "personality_tone": new_personality,
            "personality_transition": personality_transition
        }

def _extract_follow_up_question(response_text: str) -> Optional[str]:
    """
    Extract a follow-up question from the response if present.
    
    Args:
        response_text: Full response text
    
    Returns:
        Optional[str]: Follow-up question or None
    """
    sentences = response_text.split('.')
    
    # Look for last sentence ending with "?"
    for sentence in reversed(sentences):
        if '?' in sentence:
            return sentence.strip()
    
    return None

def _should_initiate_engagement(session_data: Dict, query_type: str) -> bool:
    """
    Determine if Oracle should proactively engage after this response.
    
    Args:
        session_data: Session data
        query_type: Current query type
    
    Returns:
        bool: True if should initiate
    """
    # Don't initiate if this was a factual lookup
    factual_types = ['specific_movie', 'tell_me_more']
    if query_type in factual_types:
        return False
    
    # Initiate if conversation is getting stale (many facts, no engagement)
    conversation_turn = session_data.get("conversation_turn", 0)
    if conversation_turn >= 3:
        return True
    
    return False

def should_use_conversation_layer(query_type: str, conversation_history: List[Dict], user_query: str) -> bool:
    """
    Determine whether to use conversational layer vs RAG/lookup.
    
    Args:
        query_type: Detected query type
        conversation_history: List of previous messages
        user_query: Current user query
    
    Returns:
        bool: True if should use conversation layer
    """
    # Check if the query is asking a factual question about horror movies/characters
    # Factual questions should go to RAG, not conversation layer
    user_query_lower = user_query.lower()
    
    # Factual question patterns - questions about facts, details, characters, plots
    factual_indicators = ['is ', 'was ', 'are ', 'were ', 'what is', 'who is', 'when is', 'where is', 'what year', 'what movie', 'which movie', 'how many', 'does ', 'did ', 'do ', 'has ', 'have ', 'can ', 'could ', 'would ', 'will ', 'why is', 'why was', 'how is', 'how was', 'character', 'characters', 'director', 'actor', 'actress']
    
    # Check if it's a factual question
    is_factual_question = any(indicator in user_query_lower for indicator in factual_indicators)
    is_question = user_query.strip().endswith('?')
    
    # ALWAYS route factual questions to RAG, regardless of query type or length
    # This ensures "is jigsaw gay?" goes to RAG, not conversation layer
    if is_factual_question and is_question:
        return False
    
    # For general query type, use conversation layer
    if query_type == 'general':
        return True
    
    # Use conversation layer if query is short/ambiguous
    if len(user_query.split()) <= 3:
        return True
    
    # Use conversation layer if there's conversation history
    if len(conversation_history) >= 2:
        return True
    
    # Use conversation layer for philosophical/subjective queries
    if query_type == 'scariest':
        return True
    
    # Otherwise, use factual lookup
    return False

def create_hybrid_response(
    factual_response: str,
    conversation_data: Dict,
    movie_details: Optional[Dict] = None
) -> str:
    """
    Combine factual RAG response with conversational elements.
    
    Args:
        factual_response: Response from RAG/lookup
        conversation_data: Data from conversation node
        movie_details: Optional movie details
    
    Returns:
        str: Hybrid response
    """
    # If no conversation data, return factual
    if not conversation_data:
        return factual_response
    
    # Add follow-up question to factual response
    if conversation_data.get("follow_up_question"):
        factual_response += f"\n\n{conversation_data['follow_up_question']}"
    
    return factual_response


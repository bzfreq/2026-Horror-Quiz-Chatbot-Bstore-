"""
Proactive Engagement System
Handles Oracle initiating conversations and follow-up engagement
"""

import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Proactive message pools by personality state
PROACTIVE_MESSAGES = {
    "curious": [
        "I notice you've asked about a few classics... what draws you to the old-school horror vibe?",
        "You've explored quite a range tonight. Which subgenre actually makes you lose sleep?",
        "We've discussed the visceral stuff. What about the psychological horror that gets under your skin?",
        "Interesting choices so far. Tell me, what's your first horror memory? The one that marked you?",
        "You're wandering through the catalog. What are you really searching for tonight?"
    ],
    
    "engaged": [
        "Since you mentioned enjoying that... have you explored the director's other work?",
        "Building on what we discussed: what's the most unsettling detail you remember?",
        "You've shown taste. But what about the hidden gems most people miss?",
        "We've covered the obvious picks. Ready to go deeper into the archives?",
        "Your preferences are emerging. What if I told you there's something even better?"
    ],
    
    "philosophical": [
        "Dark question for you: do you think horror makes us stronger, or just desensitizes us?",
        "I've been wondering... why do we need the monsters? What gap does horror fill?",
        "Here's a thought: the best horror isn't about the monster. It's about what it reveals in us. Agree?",
        "Do you believe in evil as a force, or just broken people in the dark?",
        "What makes horror different from other genres? What does it do that nothing else can?"
    ],
    
    "playful": [
        "Okay, hot take time: practical effects beat CGI every time. Fight me.",
        "Real talk: who scared you more as a kid, Freddy or Jason? Wrong answers only.",
        "Plot twist: your top horror movie is actually a documentary. Discuss.",
        "If you could be any horror villain, but you gotta wear the outfit 24/7, who do you pick?",
        "Unpopular opinion: the worst horror movie is still scarier than the best rom-com. Change my mind."
    ],
    
    "eerie": [
        "I've been watching you explore... curious patterns in what you choose.",
        "Some questions linger longer than screams. What are you really afraid of?",
        "The films you seek... they say something about you. Do you know what?",
        "Every horror fan has one they can't watch twice. Which one marked you?",
        "The darkness you chase... it knows you're coming."
    ]
}

def check_initiation_triggers(session_data: Dict, last_activity_time: Optional[str] = None) -> bool:
    """
    Check if Oracle should proactively initiate a message.
    
    Args:
        session_data: Session data
        last_activity_time: Last user activity timestamp
    
    Returns:
        bool: True if should initiate
    """
    # Check idle time
    if last_activity_time:
        try:
            last_activity = datetime.fromisoformat(last_activity_time)
            idle_seconds = (datetime.now() - last_activity).total_seconds()
            
            # Initiate if idle > 30 seconds
            if idle_seconds > 30:
                return True
        except (ValueError, TypeError):
            pass
    
    # Check for pattern of factual-only exchanges
    messages = session_data.get("messages", [])
    if len(messages) >= 5:
        # Count questions in last 5 user messages
        recent_user_messages = [msg for msg in messages[-5:] if msg.get("role") == "user"]
        if len(recent_user_messages) >= 4:
            # If user has asked 4+ questions without Oracle engaging, initiate
            return True
    
    # Check conversation turn counter
    conversation_turn = session_data.get("conversation_turn", 0)
    if conversation_turn >= 3 and conversation_turn % 5 == 0:
        # Initiate every 5th turn after turn 3
        return True
    
    return False

def generate_proactive_message(
    session_context: Dict,
    personality_state: str,
    user_profile: Optional[Dict] = None
) -> Optional[str]:
    """
    Generate a proactive message based on context and personality.
    
    Args:
        session_context: Full session data
        personality_state: Current Oracle personality state
        user_profile: User's horror profile
    
    Returns:
        Optional[str]: Proactive message or None
    """
    # Get message pool for personality
    message_pool = PROACTIVE_MESSAGES.get(personality_state, PROACTIVE_MESSAGES["curious"])
    
    # Personalized messages based on user profile
    if user_profile:
        horror_profile = user_profile.get("horror_profile", "")
        genre_searches = user_profile.get("genre_searches", {})
        
        if horror_profile and horror_profile != "New Horror Fan":
            personalized_messages = {
                "curious": [
                    f"You're a {horror_profile}... what draws you to that darkness?",
                    f"Interesting profile. As a {horror_profile}, what's missing from your collection?",
                    f"Fellow {horror_profile}... ready to explore beyond the obvious?"
                ],
                "engaged": [
                    f"Since you're a {horror_profile}, you've probably seen the staples. What about the deep cuts?",
                    f"Your {horror_profile} taste shows. But what terrified you more than expected?",
                    f"As a {horror_profile}, what's the one movie that surprised you?"
                ]
            }
            
            if personality_state in personalized_messages:
                message_pool = personalized_messages[personality_state] + message_pool
    
    # Return random message from pool
    return random.choice(message_pool)

def detect_engagement_opportunity(
    session_data: Dict,
    recent_messages: List[Dict]
) -> Optional[str]:
    """
    Detect opportunities for Oracle to engage based on conversation flow.
    
    Args:
        session_data: Session data
        recent_messages: Recent message history
    
    Returns:
        Optional[str]: Engagement opportunity type or None
    """
    if not recent_messages:
        return None
    
    # Check for factual answer that needs follow-up
    last_oracle_message = None
    for msg in reversed(recent_messages):
        if msg.get("role") == "assistant":
            last_oracle_message = msg.get("content", "")
            break
    
    if last_oracle_message:
        # If Oracle just gave facts without engagement, suggest follow-up
        if len(last_oracle_message.split('.')[:3]) > 0 and '?' not in last_oracle_message:
            return "factual_response_needs_followup"
    
    # Check for user showing enthusiasm
    last_user_message = recent_messages[-1] if recent_messages else None
    if last_user_message:
        content_lower = last_user_message.get("content", "").lower()
        enthusiasm_words = ["love", "amazing", "awesome", "great", "epic", "wow", "!"]
        if any(word in content_lower for word in enthusiasm_words):
            return "user_enthusiasm_detected"
    
    # Check for confusion/short responses
    if last_user_message:
        content_length = len(last_user_message.get("content", "").split())
        if content_length <= 3:
            return "user_needs_guidance"
    
    return None

def get_proactive_message_for_opportunity(
    opportunity_type: str,
    personality_state: str,
    session_context: Dict
) -> Optional[str]:
    """
    Get specific proactive message for an engagement opportunity.
    
    Args:
        opportunity_type: Type of engagement opportunity
        personality_state: Current personality state
        session_context: Session data
    
    Returns:
        Optional[str]: Proactive message
    """
    opportunity_messages = {
        "factual_response_needs_followup": {
            "curious": "That's the surface. Want to dive deeper into what makes it terrifying?",
            "engaged": "Beyond the facts, what emotion does that film stir in you?",
            "philosophical": "But here's the real question: why does that matter?",
            "playful": "Sure, but did you know the REAL fun fact?",
            "eerie": "Knowledge is power... but it also opens doors. Do you want the full truth?"
        },
        "user_enthusiasm_detected": {
            "curious": "Your passion is infectious. What else ignites that fire?",
            "engaged": "YES! That energy. Tell me more about why it hits you like that.",
            "philosophical": "Enthusiasm like yours... it reveals something deeper. What draws you to that intensity?",
            "playful": "I live for this energy! What else gets you this hyped?",
            "eerie": "Ah, you've felt the pull. The darkness recognizes you."
        },
        "user_needs_guidance": {
            "curious": "I sense uncertainty. What are you truly looking for?",
            "engaged": "Let me help focus your search. What's the vibe you want?",
            "philosophical": "The question is the beginning. What's the fear you're chasing?",
            "playful": "Playing coy? Fine. I'll tease it out of you. Top 3 horror movies?",
            "eerie": "You hesitate. Why? What aren't you saying?"
        }
    }
    
    state_messages = opportunity_messages.get(opportunity_type, {})
    return state_messages.get(personality_state, None)

def should_auto_append_followup(query_type: str, response_type: str) -> bool:
    """
    Determine if a follow-up question should be auto-appended to a response.
    
    Args:
        query_type: Type of user query
        response_type: Type of response generated
    
    Returns:
        bool: True if should append follow-up
    """
    # Always append for factual lookups
    if query_type in ['specific_movie', 'tell_me_more']:
        return True
    
    # Append for category recommendations
    if query_type in ['zombies', 'vampires', 'slashers', 'bloodiest']:
        return True
    
    # Don't append for general conversational responses (already has questions)
    if query_type == 'general':
        return False
    
    return False






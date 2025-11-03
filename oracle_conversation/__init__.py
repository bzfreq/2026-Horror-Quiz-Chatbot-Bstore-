"""
Horror Oracle Conversation Layer
Handles natural dialogue, personality states, and proactive engagement
"""

from .conversation_memory import (
    init_session, 
    get_session, 
    update_session,
    add_message_to_session,
    build_conversation_context,
    cleanup_old_sessions,
    sync_sessions,
    load_user_profile
)
from .oracle_conversation_node import (
    oracle_conversation_node,
    should_use_conversation_layer
)
from .personality_engine import (
    determine_personality_state,
    get_personality_prompt,
    PERSONALITY_STATES
)
from .proactive_engagement import (
    check_initiation_triggers,
    generate_proactive_message
)

__all__ = [
    'init_session',
    'get_session', 
    'update_session',
    'add_message_to_session',
    'build_conversation_context',
    'cleanup_old_sessions',
    'sync_sessions',
    'load_user_profile',
    'oracle_conversation_node',
    'should_use_conversation_layer',
    'determine_personality_state',
    'get_personality_prompt',
    'PERSONALITY_STATES',
    'check_initiation_triggers',
    'generate_proactive_message'
]


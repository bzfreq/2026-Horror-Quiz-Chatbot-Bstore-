# 🩸 HORROR ORACLE – CONVERSATIONAL LAYER IMPLEMENTATION PLAN

## PROJECT OVERVIEW

**Current State:** Horror Oracle is a Flask + JavaScript web app that retrieves movie data from OMDB/TMDB, answers horror movie questions via RAG (ChromaDB vector store), and uses a temporary vector index for contextual memory. It has visual atmosphere (horror stills, "Face Your Nightmares" button) but lacks natural conversational flow.

**Goal:** Add an immersive conversational layer that makes the Oracle **talk naturally** with the user—engaging with curiosity, eerie insights, and questions. The Oracle should sometimes **steer the conversation itself**, not wait passively.

---

## ARCHITECTURE ANALYSIS

### Current Flow (Lines 795-885 in `horror.py`):

1. **Entry Point:** `/ask-oracle` Flask endpoint
2. **Query Analysis:** `detect_query_type()` categorizes input (movie lookup, bloodiest, zombies, etc.)
3. **Response Generation:** 
   - RAG chain retrieves context from ChromaDB
   - `generate_oracle_response()` uses LangChain LCEL pattern
   - `generate_conversational_response()` handles specific categories
4. **Memory:** Temporary vector index (ChromaDB) with 4-document retrieval
5. **Frontend:** `index.html` shows chat interface with `addChatMessage()` — **no conversation history storage**

### Key Constraints:
- **No session tracking** between messages
- **No conversation history** passed to LLM
- Responses are stateless (each message is independent)
- ChromaDB vector retrieval provides context but no dialogue memory

---

## IMPLEMENTATION PLAN

### **PHASE 1: CONVERSATION MEMORY LAYER**

#### 1.1 Session Storage Structure

**Location:** New module `oracle_conversation/conversation_memory.py`

**Storage:** In-memory dictionary with optional persistence file
```python
conversation_sessions = defaultdict(lambda: {
    "messages": [],  # List of {role, content, timestamp}
    "context_summary": "",  # Last 3-5 message summary
    "user_profile": {},  # Horror preferences from user_data.json
    "last_movie_discussed": None,
    "conversation_turn": 0,
    "oracle_personality_state": "curious"  # curious, engaged, philosophical, playful
})
```

**Session ID Generation:**
- Extract `googleId` from request if available
- Fallback to `session_id` from frontend (generate UUID on first load)
- Store in `user_data.json` under `conversation_sessions`

#### 1.2 Memory Context Builder

**Function:** `build_conversation_context(session_id, current_query)`

**Logic:**
1. Load last 5 messages from session
2. If >5 messages, create 2-sentence summary of older context
3. Extract key entities: movies mentioned, user preferences, topics discussed
4. Return formatted string for LLM prompt injection

**Output Format:**
```
Previous conversation context:
- User prefers slasher movies and mentioned enjoying Halloween
- Oracle recommended The Exorcist (psychological horror)
- Last discussed: "What makes a good horror movie?"

Previous Oracle responses:
- "Horror works when it plays with fear of the unknown..."
- "The Exorcist is brilliant because it shows evil in the ordinary..."
```

---

### **PHASE 2: CONVERSATION LAYER NODE**

#### 2.1 New Function: `oracle_conversation_node()`

**Location:** Add to `horror.py` after `generate_conversational_response()` (line 572)

**Signature:**
```python
def oracle_conversation_node(user_query, session_id, conversation_history, query_type):
    """
    Generate natural, conversational Oracle response with memory context.
    
    Args:
        user_query: Current user message
        session_id: Unique session identifier
        conversation_history: List of previous messages
        query_type: Detected query category
        
    Returns:
        dict: {
            "response": str,  # Oracle's conversational reply
            "follow_up_question": str,  # Optional question to keep conversation going
            "should_initiate": bool,  # Whether Oracle should proactively engage
            "personality_tone": str  # curious/engaged/philosophical/playful
        }
    """
```

#### 2.2 Trigger Conditions

**When to use conversational layer vs. RAG/factual lookup:**

1. **Use conversational layer when:**
   - Query type is `'general'` (not movie-specific)
   - Query type is `'scariest'` (subjective opinion)
   - User asks open-ended philosophical questions
   - Conversation history shows 2+ previous exchanges
   - Message is short (<5 words) or ambiguous

2. **Use existing RAG lookup when:**
   - Query type is `'specific_movie'` (factual lookup)
   - Query type is `'tell_me_more'` (deeper dive into known movie)
   - Query type is category-based (`'zombies'`, `'slashers'`, etc.)

3. **Hybrid approach:**
   - Do factual lookup first
   - Wrap response in conversational layer for natural follow-up

---

### **PHASE 3: ORACLE PERSONALITY ENGINE**

#### 3.1 Personality System

**States:** Oracle rotates through personality states based on conversation flow

| State | Characteristics | Trigger |
|-------|----------------|---------|
| **Curious** | Asks exploratory questions, tests boundaries | Beginning of conversation, neutral queries |
| **Engaged** | Shares enthusiasm, reacts to user interests | User shows specific preferences |
| **Philosophical** | Discusses deeper themes, existential horror | After 4+ messages, abstract questions |
| **Playful** | Witty banter, references, dark humor | Light topics, humor detected in user input |
| **Eerie** | Drops unsettling insights, foreshadowing | Horror philosophy questions, night-time sessions |

**State Transitions:**
- Track message count and topic shifts
- Detect user mood from language (enthusiasm, fear, curiosity)
- Rotate every 3-5 messages to prevent monotony

#### 3.2 Response Generation Prompts

**System Prompt Template (update `get_conversational_prompt()` function):**

```python
ORACLE_CONVERSATION_PROMPTS = {
    "curious": """You are the Horror Oracle awakening to a new conversation. 
    Speak with intelligent curiosity. Ask thoughtful questions about what scares them most, 
    what drew them to horror, or what they're seeking tonight. Keep responses to 2-3 sentences. 
    End with a question that invites deeper dialogue.""",
    
    "engaged": """You are the Horror Oracle, fully engaged in the conversation. 
    The user has shown genuine interest in horror. Share your enthusiasm, make connections 
    between their preferences, recommend hidden gems, and show you're listening. 
    Reference previous topics naturally. Keep responses to 2-3 sentences. End with a question or observation.""",
    
    "philosophical": """You are the Horror Oracle contemplating the deeper nature of fear and horror. 
    Discuss themes: why we're drawn to horror, what it reveals about humanity, the line between terror and catharsis. 
    Be thoughtful but not pretentious. Keep responses to 3-4 sentences. End with a philosophical question or insight.""",
    
    "playful": """You are the Horror Oracle with a wicked sense of humor. 
    You love horror and enjoy playful banter with fellow fans. Drop pop culture references, 
    make dark jokes, celebrate the absurdity of horror tropes. Keep responses to 2-3 sentences. 
    End with a playful question or humorous observation.""",
    
    "eerie": """You are the Horror Oracle revealing unsettling truths. 
    Speak with quiet intensity. Drop foreshadowing comments, make the mundane sound sinister, 
    hint at deeper knowledge of the darkness. Keep responses to 2-3 sentences. 
    End with an eerie question or unsettling observation."""
}
```

---

### **PHASE 4: PROACTIVE ENGAGEMENT SYSTEM**

#### 4.1 Initiation Triggers

**Oracle should proactively engage when:**
- **Idle detection:** 30+ seconds without user message (frontend check)
- **After factual answers:** Automatically append follow-up question
- **Pattern breaks:** User asks 3+ factual questions in a row → Oracle shifts to curiosity
- **Silent sessions:** Oracle hasn't spoken in 5+ user messages

#### 4.2 Initiation Messages Pool

**Function:** `generate_proactive_message(session_context, personality_state)`

**Example Outputs:**
```python
PROACTIVE_MESSAGES = {
    "curious": [
        "I notice you've asked about a few classics... what draws you to the old-school horror vibe?",
        "You've explored quite a range tonight. Which subgenre actually makes you lose sleep?",
        "We've discussed the visceral stuff. What about the psychological horror that gets under your skin?"
    ],
    "philosophical": [
        "Dark question for you: do you think horror makes us stronger, or just desensitizes us?",
        "I've been wondering... why do we need the monsters? What gap does horror fill?",
        "Here's a thought: the best horror isn't about the monster. It's about what it reveals in us. Agree?"
    ],
    "playful": [
        "Okay, hot take time: practical effects beat CGI every time. Fight me.",
        "Real talk: who scared you more as a kid, Freddy or Jason? Wrong answers only.",
        "Plot twist: your top horror movie is actually a documentary. Discuss."
    ]
}
```

---

### **PHASE 5: INTEGRATION FLOW**

#### 5.1 Modified `/ask-oracle` Endpoint Flow

**Current Flow (Lines 795-885):**
1. Extract user input
2. Detect query type
3. Generate RAG response OR category response
4. Return JSON

**New Flow:**
```
1. Extract user input + session_id (from request)
2. Load conversation history from session storage
3. Detect query type
4. DECISION TREE:
   
   IF query_type in ['specific_movie', 'tell_me_more']:
       → Run existing RAG/factual lookup
       → Get factual response
       → Pass to conversational wrapper
   ELIF query_type == 'general' or len(conversation_history) >= 2:
       → Use oracle_conversation_node() as PRIMARY
       → Optionally run RAG in background for context
   ELSE:
       → Hybrid: RAG + conversational layer

5. Update conversation history in session
6. Return {
    "response": str,
    "follow_up_question": str (optional),
    "movie_details": dict (if applicable),
    "recommendations": list,
    "conversation_turn": int,
    "oracle_personality": str
}
```

#### 5.2 Frontend Integration (`index.html`)

**Add session tracking:**
```javascript
// Generate session ID on load (if not exists)
let sessionId = sessionStorage.getItem('oracle_session_id');
if (!sessionId) {
    sessionId = generateUUID();
    sessionStorage.setItem('oracle_session_id', sessionId);
}

// Send session_id with every request
async function sendMessage() {
    const query = userInput.value.trim();
    // ... existing code ...
    
    const response = await fetch(`${API_BASE}/ask-oracle`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ 
            query: query,
            session_id: sessionId,
            google_id: user?.sub || null
        })
    });
    
    const data = await response.json();
    
    // Handle follow-up question
    if (data.follow_up_question) {
        // Optionally auto-append or show as suggested prompt
        showSuggestedQuestion(data.follow_up_question);
    }
}
```

**Proactive initiation check:**
```javascript
// After 30 seconds of inactivity
let idleTimer;
userInput.addEventListener('input', () => {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => {
        // Trigger Oracle proactive message
        checkOracleInitiation(sessionId);
    }, 30000);
});
```

---

### **PHASE 6: DATA FLOW BETWEEN NODES**

#### 6.1 Shared Data Structure

```python
conversation_context = {
    "session_id": str,
    "user_id": str,  # google_id if available
    "current_query": str,
    "query_type": str,
    "conversation_history": list,  # Last 5 messages
    "retrieved_context": list,  # From ChromaDB if applicable
    "user_profile": dict,  # Horror preferences
    "current_movie": str,  # If discussing specific movie
    "personality_state": str,
    "conversation_turn": int
}
```

#### 6.2 Node Interaction

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND REQUEST                         │
│  {query, session_id, google_id}                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                  /ask-oracle ENDPOINT                        │
│  • Load conversation history                                │
│  • Detect query type                                        │
│  • Build conversation context                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴──────────────────┐
        ↓                                    ↓
┌──────────────────────┐          ┌──────────────────────────┐
│  RAG NODE            │          │  CONVERSATION NODE        │
│  (ChromaDB lookup)   │          │  (Personality engine)     │
│  • Retrieve docs     │          │  • Generate personality   │
│  • Generate facts    │◄─────────┤    response               │
└──────────────────────┘          │  • Create follow-up Q     │
        ↓                         │  • Check init triggers    │
        └────────► HYBRID ───────►└──────────────────────────┘
                    ↓
        ┌──────────────────────────────────────┐
        │  RESPONSE SYNTHESIS                  │
        │  • Merge factual + conversational    │
        │  • Add follow-up question            │
        │  • Update session history            │
        │  • Return to frontend                │
        └──────────────────────────────────────┘
```

---

## IMPLEMENTATION SUMMARY

### **New Functions to Create:**

1. **`oracle_conversation_node()`** - Main conversation handler
2. **`build_conversation_context()`** - Memory context builder
3. **`update_conversation_session()`** - Session persistence
4. **`should_use_conversation_layer()`** - Trigger decision logic
5. **`generate_proactive_message()`** - Proactive engagement
6. **`determine_personality_state()`** - Personality state machine

### **Modified Functions:**

1. **`ask_oracle()`** - Add session loading, decision tree logic, hybrid flow
2. **`get_conversational_prompt()`** - Expand with personality system
3. **`detect_query_type()`** - Add "general" catch-all detection

### **New Data Structures:**

1. **`conversation_sessions`** - In-memory session storage
2. **`ORACLE_CONVERSATION_PROMPTS`** - Personality prompts dict
3. **`PROACTIVE_MESSAGES`** - Initiation message pools
4. **Session persistence** - `conversation_sessions.json` file

### **Frontend Changes:**

1. **Session ID generation** and persistence
2. **Send session_id** with every `/ask-oracle` request
3. **Display follow-up questions** as suggested prompts
4. **Idle timer** for proactive engagement check

---

## INTEGRATION CHECKLIST

- [ ] Create `oracle_conversation/` module directory
- [ ] Implement conversation memory storage (in-memory + file backup)
- [ ] Build conversation context builder function
- [ ] Create oracle_conversation_node with personality system
- [ ] Add proactive engagement logic
- [ ] Modify `/ask-oracle` endpoint with decision tree
- [ ] Update frontend to send session_id
- [ ] Add follow-up question UI elements
- [ ] Test session persistence across page refreshes
- [ ] Test personality state transitions
- [ ] Test hybrid RAG + conversation responses
- [ ] Add error handling for session loading failures

---

## SUCCESS METRICS

**Conversational Quality:**
- Oracle asks relevant follow-up questions in 80%+ of responses
- Responses reference previous conversation naturally
- Personality state shifts feel organic, not jarring

**Engagement:**
- Proactive messages trigger 40%+ response rate
- Average session length increases by 2+ messages
- User returns to continue conversations

**Technical:**
- Session persistence works across refreshes
- Memory load < 100MB per 100 concurrent sessions
- Response time < 2 seconds for conversational layer

---

## FILE STRUCTURE

```
C:\31000\
├── horror.py                          # Main app (modified)
├── oracle_conversation/               # NEW MODULE
│   ├── __init__.py
│   ├── conversation_memory.py        # Session storage & context
│   ├── oracle_conversation_node.py   # Main conversation engine
│   ├── personality_engine.py         # State machine & prompts
│   └── proactive_engagement.py       # Initiation triggers
├── conversation_sessions.json        # NEW: Session persistence
├── user_data.json                     # Existing (enhanced)
├── index.html                         # Frontend (modified)
└── HORROR_ORACLE_CONVERSATION_LAYER_PLAN.md  # This file
```

---

## NEXT STEPS

**This plan is a structural blueprint—no code yet.**

**Recommended implementation order:**
1. **Start with conversation memory** (Phase 1) - Foundation for everything else
2. **Build core conversation node** (Phase 2) - Test with basic responses
3. **Add personality system** (Phase 3) - Layer personality on top
4. **Implement proactive engagement** (Phase 4) - Advanced feature
5. **Integrate with existing flow** (Phase 5) - Connect all pieces
6. **Test thoroughly** (Phase 6) - Refine based on real usage

**Ready to transform Horror Oracle from a Q&A tool into a living, conversational AI companion.** 🩸


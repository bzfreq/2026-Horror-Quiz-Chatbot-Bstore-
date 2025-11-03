# RLOM (Reinforcement Learning with Optimized Memories) Setup Prompt

## CONTEXT AND BACKGROUND

I have a Horror Oracle chatbot system built with Flask, Python, and OpenAI's API. The system currently has:
- FAISS-based semantic memory (TemporaryMemory class) that stores conversation messages and retrieves relevant context using embeddings
- Redis store for session persistence (RedisStore class)
- A conversation layer (`oracle_conversation`) that manages conversational flow
- RAG system using ChromaDB for horror movie knowledge
- Multiple endpoints including `/oracle_converse` and `/ask-oracle` for user interactions

The current memory system works for individual sessions, but I need to implement RLOM to:
1. **Persistently remember important context across 20+ separate conversations** - Users should be able to mention a movie, character, or preference once, and the system should remember it in future conversations without me having to re-explain it
2. **Automatically determine what information is "important enough" to remember** - The system should learn which facts, preferences, entities, and context should be stored in long-term memory vs. temporary session memory
3. **Optimize memory retrieval** - When a user mentions something vaguely or uses pronouns (he, she, it, the movie), the system should automatically link it to previously discussed entities from ANY prior conversation, not just the current session
4. **Handle language variations** - The system should understand that "The Exorcist", "Exorcist", "that possession movie", "the one with Regan", etc. all refer to the same movie, even across different conversation sessions
5. **Build a knowledge graph of relationships** - Remember connections between movies, directors, actors, genres, user preferences, and how they relate to each other

## CURRENT CODEBASE STRUCTURE

### Key Files:
- `horror.py` - Main Flask application (2310 lines)
- `oracle_engine/memory.py` - TemporaryMemory class using FAISS for semantic search
- `oracle_engine/memory_store.py` - RedisStore for session persistence
- `oracle_conversation/` - Conversation layer module

### Current Memory Implementation:
```python
# From oracle_engine/memory.py
class TemporaryMemory:
    - Uses FAISS IndexFlatL2 for vector similarity search
    - Stores messages as embeddings + text
    - Retrieves top_k most similar messages based on query embedding
    - Clears when session ends (no persistence across sessions)
```

### Current Limitations:
1. **No cross-session memory** - Each conversation session is isolated
2. **No entity resolution** - System doesn't maintain a persistent database of discussed entities (movies, characters, preferences)
3. **No importance scoring** - All messages stored equally, no mechanism to determine what's "important"
4. **No relationship tracking** - Doesn't remember connections between entities
5. **Manual context management** - I have to manually write prompts that reference previous conversations

## REQUIREMENTS FOR RLOM IMPLEMENTATION

### 1. Persistent Entity Memory System
- Create a long-term memory store (can use SQLite, PostgreSQL, or extend Redis) that persists across sessions
- Store entities with unique IDs and metadata:
  - Movies: title, year, directors, actors, genres, user preferences about it
  - Characters: name, movie association, user reactions
  - User Preferences: favorite genres, horror tolerance, preferred subgenres
  - Topics: recurring discussion themes
- Each entity should have:
  - Canonical name (e.g., "The Exorcist")
  - Aliases/variations (e.g., "Exorcist", "that possession movie", "the one with Regan")
  - Associated metadata (year, director, etc.)
  - Relationship links to other entities
  - Last discussed timestamp
  - Discussion frequency
  - User sentiment/opinion about it (if expressed)

### 2. Importance Scoring & Memory Optimization
- Implement a scoring system to determine what to remember:
  - **Explicit mentions** - User says "I love The Exorcist" (high importance)
  - **Entity specificity** - Specific movie titles vs. generic "horror movie" (high vs. low)
  - **Discussion depth** - Extended conversations about something (high importance)
  - **Preference indicators** - Words like "love", "hate", "favorite", "avoid" (very high importance)
  - **Repeated mentions** - If user mentions something multiple times across sessions (very high importance)
  - **Question context** - Questions about something indicate interest (medium-high importance)
- Only store high-importance facts in persistent memory
- Use temporary session memory for low-importance context

### 3. Intelligent Entity Resolution
- When user mentions a pronoun or vague reference, use entity resolution:
  - Check current session conversation history
  - Query persistent entity memory for recent entities
  - Use semantic similarity to match vague descriptions ("that scary movie with the kid" → "The Exorcist")
  - Resolve "it", "he", "she", "they", "that movie", "the one we talked about" to actual entities
- Build a resolution cache for common patterns

### 4. Relationship Graph
- Maintain a graph database or relationship table:
  - Movie → Director relationships
  - Movie → Genre relationships
  - Movie → Similar Movies (based on user discussions)
  - User Preference → Movie associations
  - Temporal relationships (sequels, prequels, remakes)
- Use this for intelligent recommendations and context building

### 5. Memory Retrieval Optimization
- When processing a new user query:
  1. Extract potential entity mentions (using NER if possible, or pattern matching)
  2. Query persistent entity memory for matches
  3. Retrieve related entities from relationship graph
  4. Combine with session-specific FAISS retrieval
  5. Rank and deduplicate results
  6. Build comprehensive context string for LLM

### 6. Language Variation Handling
- Implement canonicalization:
  - "The Exorcist" = "Exorcist" = "that exorcism movie" = "the William Friedkin film"
- Use fuzzy matching, embedding similarity, and alias resolution
- Build an alias dictionary that grows over time

### 7. Conversation Context Builder
- Create a function that builds optimal context from:
  - Current session messages (last 10-15 messages from FAISS)
  - Relevant entities from persistent memory (matched by current query)
  - Relationship context (related movies, user preferences)
  - Historical conversation summaries (condensed versions of past discussions)
- This context should be injected into LLM prompts automatically

### 8. Memory Maintenance
- Implement memory pruning:
  - Remove low-importance facts after N days of no mention
  - Archive old conversation summaries
  - Keep high-importance facts indefinitely
- Implement memory consolidation:
  - Merge duplicate entities
  - Update entity metadata when new information arrives
  - Resolve conflicts (if user says contradictory things)

## IMPLEMENTATION APPROACH

### Phase 1: Entity Memory Database
1. Create a new module `oracle_engine/persistent_memory.py` with:
   - `EntityMemory` class that stores entities in SQLite/PostgreSQL
   - Methods: `store_entity()`, `retrieve_entity()`, `search_entities()`, `link_entities()`
   - Schema: entities table (id, type, canonical_name, aliases_json, metadata_json, importance_score, last_mentioned, created_at)
   - Schema: relationships table (entity1_id, entity2_id, relationship_type, strength)

### Phase 2: Importance Scorer
1. Create `oracle_engine/importance_scorer.py`:
   - `score_message_importance()` function that analyzes a message and returns importance score (0-100)
   - Factors: explicit entity mentions, preference words, question depth, specificity
   - Extract entities from messages (movies, preferences, topics)

### Phase 3: Entity Resolution Engine
1. Create `oracle_engine/entity_resolver.py`:
   - `resolve_pronoun()` - Resolves "it", "he", "she", etc. to entities
   - `resolve_vague_reference()` - Resolves "that movie", "the one we discussed" to specific entities
   - `canonicalize_name()` - Converts variations to canonical names
   - Uses semantic similarity + alias matching + recency

### Phase 4: Memory Integration
1. Modify `horror.py`:
   - Import new RLOM modules
   - In `/oracle_converse` and `/ask-oracle` endpoints:
     - Extract entities from user input
     - Score importance of current conversation
     - Store high-importance facts in persistent memory
     - Retrieve relevant entities before generating response
     - Build comprehensive context with persistent + session memory
   - Update prompt templates to include persistent entity context

### Phase 5: Context Builder
1. Create `oracle_engine/context_builder.py`:
   - `build_conversation_context()` function that:
     - Gets recent session messages from FAISS
     - Retrieves relevant entities from persistent memory
     - Fetches related entities via relationship graph
     - Combines into optimal context string
     - Handles token limits intelligently

## SPECIFIC CODE REQUIREMENTS

### Entity Memory Schema (SQLite)
```sql
CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,  -- 'movie', 'character', 'preference', 'topic', etc.
    canonical_name TEXT NOT NULL,
    aliases TEXT,  -- JSON array of alternative names
    metadata TEXT,  -- JSON object with type-specific data
    importance_score REAL DEFAULT 50.0,
    last_mentioned TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mention_count INTEGER DEFAULT 1
);

CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity1_id TEXT NOT NULL,
    entity2_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,  -- 'similar_to', 'directed_by', 'features', 'user_likes', etc.
    strength REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entity1_id) REFERENCES entities(id),
    FOREIGN KEY (entity2_id) REFERENCES entities(id)
);

CREATE INDEX idx_entities_type ON entities(type);
CREATE INDEX idx_entities_last_mentioned ON entities(last_mentioned DESC);
CREATE INDEX idx_relationships_entity1 ON relationships(entity1_id);
CREATE INDEX idx_relationships_entity2 ON relationships(entity2_id);
```

### Integration Points in horror.py

1. **In `/oracle_converse` endpoint (around line 909):**
   - After retrieving FAISS context, also query persistent entity memory
   - Resolve pronouns/vague references using entity resolver
   - Store any new important entities mentioned
   - Build enhanced context with persistent memory

2. **In `/ask-oracle` endpoint (around line 1049):**
   - Same entity resolution and memory integration
   - Store movie preferences when user discusses movies
   - Link movies to genres, directors, etc. automatically

3. **Prompt Template Updates:**
   - Current prompt (line 941) should include:
     ```
     PERSISTENT MEMORY CONTEXT:
     [Relevant entities from previous conversations]
     
     ENTITY RESOLUTIONS:
     [Pronouns resolved to actual entities]
     
     USER PREFERENCES:
     [Stored preferences that relate to current query]
     ```

## EDGE CASES TO HANDLE

1. **Contradictory Information:**
   - User says "I hate The Exorcist" in session 1
   - User says "I love The Exorcist" in session 15
   - Solution: Update preference with timestamp, store both sentiments with recency weighting

2. **Ambiguous References:**
   - User says "that movie" when multiple movies were discussed
   - Solution: Use recency + context similarity to disambiguate

3. **Entity Merging:**
   - "Exorcist" and "The Exorcist" should be same entity
   - Solution: Canonicalization on storage, fuzzy matching on retrieval

4. **Memory Limits:**
   - Too many entities stored, retrieval becomes slow
   - Solution: Prune low-importance entities, use importance-based retrieval limits

5. **Multiple Users:**
   - System should handle multiple users with separate entity memories
   - Solution: Add `user_id` or `session_group_id` to entity storage (optional, for multi-user systems)

## TESTING REQUIREMENTS

After implementation, I should be able to:
1. Have conversation about "The Exorcist" in session 1
2. Start new session (session 2) and say "tell me more about it" - system should know "it" = "The Exorcist"
3. Say "what other movies are similar?" - system should remember we discussed The Exorcist and recommend similar possession movies
4. Have 20 different conversations about different topics, then return to The Exorcist discussion and system remembers everything
5. Use vague references like "that scary movie", "the one with the kid", etc. and system resolves correctly

## EXPECTED BEHAVIOR AFTER IMPLEMENTATION

When a user sends a message, the system should:
1. **Parse the message** to extract potential entity mentions
2. **Resolve pronouns/vague references** to specific entities from persistent memory
3. **Retrieve relevant entities** that relate to the current query
4. **Score importance** of current message to determine if anything should be stored
5. **Store important facts** in persistent memory with proper relationships
6. **Build comprehensive context** combining:
   - Recent session messages (FAISS)
   - Relevant persistent entities
   - Relationship context
   - User preferences
7. **Generate response** using enhanced context
8. **Update entity metadata** (last_mentioned timestamp, mention_count)

## LANGUAGE AND COMMUNICATION SPECIFICATIONS

The system should handle:
- **English language** primarily (but design should allow for multi-language expansion)
- **Colloquial speech**: "that one", "the movie we talked about", "you know, the scary one"
- **Abbreviations**: "Exorcist" for "The Exorcist", "Halloween" for "Halloween (1978)"
- **Temporal references**: "last time", "earlier", "before" should resolve to previous conversations
- **Comparative references**: "similar movies", "better than that", "like the one you mentioned"
- **Possessive references**: "my favorite", "the one I liked", should link to user preferences
- **Questions that imply memory**: "What did we say about...", "Tell me more about it", "Remember when..."

## INTEGRATION WITH EXISTING CODE

The RLOM system should:
- **NOT break existing functionality** - All current endpoints should continue working
- **Enhance, don't replace** - FAISS memory should still work for session-specific context
- **Be opt-in initially** - Can be disabled if needed for testing
- **Have fallback mechanisms** - If persistent memory fails, fall back to session-only memory
- **Be thread-safe** - Multiple concurrent requests should not corrupt entity memory
- **Have logging** - Log entity storage, retrieval, and resolution for debugging

## PERFORMANCE CONSIDERATIONS

- Entity retrieval should be fast (< 100ms)
- Use database indexes on frequently queried fields
- Cache recent entity resolutions to avoid repeated queries
- Batch entity storage operations when possible
- Use async operations for non-critical memory updates

## SUCCESS CRITERIA

RLOM is successfully implemented when:
1. ✅ User can have 20+ separate conversations and system remembers discussed entities
2. ✅ Pronouns automatically resolve to previously discussed entities
3. ✅ Vague references ("that movie", "the one we talked about") resolve correctly
4. ✅ User preferences persist across sessions
5. ✅ System can answer "what did we discuss about X?" even after many other conversations
6. ✅ No need to manually rewrite prompts explaining context - system retrieves it automatically
7. ✅ Memory storage is optimized (only important facts stored)
8. ✅ Entity relationships are tracked and used for recommendations

---

**IMPORTANT:** This prompt is designed to be comprehensive enough that once RLOM is implemented, I should be able to have natural conversations with the LLM about horror movies, entities, preferences, etc., without having to re-explain context in every conversation. The system should "remember" like a human would remember previous conversations about the same topics.







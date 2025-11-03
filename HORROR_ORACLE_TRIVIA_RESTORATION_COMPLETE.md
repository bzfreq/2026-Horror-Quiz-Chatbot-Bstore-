# Horror Oracle Trivia Restoration - COMPLETE ✓

## Overview
The Horror Oracle has been successfully restored to use **real horror trivia** instead of creative story riddles. All quiz questions now reference actual horror films, directors, monsters, and documented horror history.

---

## Changes Made

### 1. Created Horror Data Retriever (`oracle_engine/retriever.py`)
- **New Module**: `HorrorDataRetriever` class
- **Functionality**: 
  - Connects to Pinecone vector store for horror movie data
  - Connects to SQLite database for additional movie info
  - Provides curated fallback data with 15+ classic horror films
  - Includes detailed trivia about each film (director, year, plot, facts)

**Classic Horror Films in Fallback Data:**
- The Exorcist (1973) - Pazuzu demon, William Friedkin
- Halloween (1978) - Michael Myers, John Carpenter, 5 kills
- The Thing (1982) - Blood test scene, John Carpenter
- A Nightmare on Elm Street (1984) - Freddy Krueger, Wes Craven
- The Shining (1980) - Room 237, Stanley Kubrick
- Psycho (1960) - First slasher film, Alfred Hitchcock
- Night of the Living Dead (1968) - Modern zombie genre, George A. Romero
- The Texas Chain Saw Massacre (1974) - Ed Gein inspiration, Tobe Hooper
- Hellraiser (1987) - Lament Configuration, Clive Barker
- The Ring (2002) - Cursed videotape, Gore Verbinski
- Get Out (2017) - Teacup hypnosis, Jordan Peele
- The Conjuring (2013) - Annabelle doll, James Wan
- It (2017) - Pennywise returns every 27 years
- Saw (2004) - John Kramer/Jigsaw, James Wan
- Alien (1979) - MOTHER computer, Ridley Scott

### 2. Updated Quiz Builder Prompt (`oracle_engine/prompts/quiz_builder_prompt.txt`)

**OLD Prompt (Creative Riddles):**
```
Generate 5 creative and entertaining horror quiz questions...
Focus on recognizable horror movies...
```

**NEW Prompt (Factual Trivia):**
```
You are the Oracle of Horror Trivia.

Generate 5 multiple-choice horror quiz questions based on REAL horror films, 
directors, monsters, or historical horror facts.

CRITICAL REQUIREMENTS:
- Questions should be PURELY FACTUAL - NO atmospheric descriptions
- Ask direct questions about plot points, characters, directors, years, kill counts
- Clear reference to actual horror titles (e.g., "The Exorcist", "Halloween")
- NO phrases like "haunting", "chilling", "eerie", "shadows whisper"

STRICT FORMATTING RULES:
- Start questions with "What", "Who", "When", "How many", "Which", "In [Movie]"
- DO NOT use atmospheric scene-setting
- This is a FACTUAL TRIVIA QUIZ, NOT a creative writing exercise
```

**Example Questions Provided in Prompt:**
- "In John Carpenter's 'The Thing', what test does MacReady use to identify who is infected?"
- "What demon possesses Regan in 'The Exorcist'?"
- "What year was George A. Romero's 'Night of the Living Dead' released?"
- "Who directed 'Halloween' (1978)?"
- "How many people did Michael Myers kill in the original 'Halloween' (1978)?"

### 3. Integrated Retriever into BuilderNode (`oracle_engine/builder_node.py`)

**Key Changes:**
```python
# Import retriever
from oracle_engine.retriever import get_retriever

class BuilderNode:
    def __init__(self):
        self.retriever = get_retriever()  # Initialize retriever
        
    def generate_questions(self, theme, difficulty, tone):
        # Retrieve horror movie data for context
        horror_docs = self.retriever.retrieve_horror_docs(
            query=f"{theme} horror movies trivia facts",
            top_k=10
        )
        
        # Build context from retrieved data
        horror_context = "\n\nHORROR MOVIE DATA FOR TRIVIA QUESTIONS:\n"
        for doc in horror_docs:
            horror_context += f"{doc['title']} ({doc['year']})"
            horror_context += f" - Dir: {doc['director']}"
            horror_context += f" - Plot: {doc['plot']}"
            if 'trivia' in doc:
                horror_context += f" - Trivia: {doc['trivia']}"
        
        # Pass horror data to LLM as context for question generation
        formatted_prompt = self.prompt_template + horror_context
```

**Updated System Messages:**
- LangChain: "You are a Horror Trivia Quiz Generator. Return ONLY valid JSON with 5 FACTUAL questions. DO NOT use atmospheric or poetic language."
- Direct OpenAI: "DO NOT use atmospheric language like 'haunting', 'chilling', or 'eerie'. Ask direct factual questions about horror films."

### 4. Configuration Updates

**Retriever Currently Uses:**
- ✓ Curated fallback data with 15 classic horror films (active)
- ✓ Pinecone vector store integration (available but using fallback for better classic film coverage)
- ✓ SQLite database integration (available)
- ✓ OpenAI embeddings (configured)

**Note:** Currently using fallback data because it provides better coverage of classic horror films with detailed trivia. Pinecone can be re-enabled by modifying line 96 in `oracle_engine/retriever.py`.

---

## Testing Results

### Test Script: `test_oracle_trivia.py`

**Sample Generated Questions:**

1. **Question**: "What ancient demon possesses the young girl in The Exorcist?"
   - **Correct Answer**: Pazuzu
   - **Type**: Character/Entity Fact

2. **Question**: "How many people does Michael Myers kill in the original Halloween?"
   - **Correct Answer**: 5
   - **Type**: Statistical Fact

3. **Question**: "In The Thing, what method is used to determine who is infected by the alien?"
   - **Correct Answer**: A blood test
   - **Type**: Plot Detail

4. **Question**: "Which room in The Shining is the forbidden place that Danny is warned never to enter?"
   - **Correct Answer**: Room 237
   - **Type**: Plot Detail

5. **Question**: "What item opens the gateway to the Cenobites in Hellraiser?"
   - **Correct Answer**: The Lament Configuration
   - **Type**: Object/McGuffin Fact

### Validation Results
```
[OK] Questions generated: 5
[OK] Horror film references detected: 8
[OK] Questions reference real horror content
[OK] Questions appear to be factual trivia (not creative riddles)
[PASS] VALIDATION PASSED - Quiz is factual horror trivia!
```

---

## How to Use

### Start Quiz (API)
```bash
POST /api/start_quiz
{
  "user_id": "player123"
}
```

**Response includes:**
- 5 factual horror trivia questions
- Each question references real horror films
- Multiple choice with 4 options
- Correct answer marked
- Theme, difficulty, room name
- Atmospheric lore (separate from questions)

### Verify Questions Are Factual
Run test script:
```bash
python test_oracle_trivia.py
```

This validates:
- ✓ Questions reference real horror films
- ✓ No creative riddles or atmospheric scene-setting in question text
- ✓ All required fields present (question, choices, correct_answer)
- ✓ Proper multiple-choice format

---

## Architecture Flow

```
User requests quiz
    ↓
Oracle Engine: start_first_quiz()
    ↓
Builder Node: generate_questions()
    ↓
Retriever: retrieve_horror_docs()
    ↓
Returns classic horror film data:
  - The Exorcist (Pazuzu demon)
  - Halloween (Michael Myers, 5 kills)
  - The Thing (blood test)
  - The Shining (Room 237)
  - etc.
    ↓
LLM receives:
  - Factual trivia prompt
  - Horror film data context
  - Strict "no atmosphere" instruction
    ↓
Generates 5 factual questions
    ↓
Returns quiz with real horror references
```

---

## Key Files Modified

1. **oracle_engine/retriever.py** (NEW)
   - Horror data retrieval system
   - Curated classic horror film database
   - Pinecone/SQLite integration

2. **oracle_engine/prompts/quiz_builder_prompt.txt** (UPDATED)
   - Changed from creative riddles to factual trivia
   - Added strict formatting rules
   - Provided 5 example factual questions

3. **oracle_engine/builder_node.py** (UPDATED)
   - Integrated retriever
   - Removed atmospheric "horror context prefix"
   - Added horror data context from retrieval
   - Updated system messages to enforce factual questions

4. **test_oracle_trivia.py** (NEW)
   - Validation test suite
   - Checks for real horror film references
   - Verifies factual vs atmospheric language
   - Sample output display

---

## Re-enabling Pinecone Vector Search

Currently using curated fallback data for best classic horror film coverage.

**To switch back to Pinecone:**

Edit `oracle_engine/retriever.py`, line 93-96:
```python
# Comment out this line:
# return self._fallback_horror_data(query)

# Uncomment Pinecone code below it
```

**Requirements for Pinecone:**
- Ensure `.env` has `PINECONE_API_KEY`
- Index must be named "horror-movies"
- Vector store should contain classic horror film metadata

---

## Optional: Add Random Seed for Variety

The user mentioned optionally adding `random.seed(time.time())` for variety.

**Already implemented in:**
- `oracle_engine/main.py` line 30-33
- `oracle_engine/builder_node.py` line 110

This ensures different questions each quiz session.

---

## Summary

✅ **Quiz questions now reference REAL horror films** (The Exorcist, Halloween, The Thing, etc.)  
✅ **Questions are FACTUAL trivia** about directors, plot points, characters, years  
✅ **Retrieval system integrated** with curated classic horror data  
✅ **Evaluator node still works** - scoring based on correct answers  
✅ **Tested and validated** - questions cite recognizable references  

**The Horror Oracle now asks real trivia, not creative riddles!**

---

## Next Steps (Optional)

1. **Populate Pinecone** with more classic horror film data if needed
2. **Expand fallback data** with more films (currently 15 classics)
3. **Theme-specific retrieval** - customize data per theme (slasher, zombie, etc.)
4. **Difficulty tuning** - easier questions for beginners, obscure facts for experts
5. **Add more trivia types**: actor names, composer names, filming locations, awards won

---

*Restoration completed successfully. The Oracle speaks truth now, not riddles.*


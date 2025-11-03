# Horror Oracle Engine - Builder & Evaluator Nodes

## Overview

The Horror Oracle Engine consists of LangGraph nodes that generate dynamic horror quiz questions and evaluate player answers with atmospheric feedback.

## Components Created

### 1. Question Generator (Builder Node)

**File**: `builder_node.py`

**Purpose**: Generates 5 horror-themed multiple-choice questions using LangChain and a sophisticated prompt template.

**Key Features**:
- Generates questions with specific theme, difficulty (0.1-1.0), and tone
- 6 atmospheric tones: creepy, mocking, ancient, whispered, grim, playful
- Themes: lore, movie, psychological, survival, slasher, monster, ghost, cosmic_horror, etc.
- Includes Oracle "Easter egg" whispers in one question per set
- Falls back to hardcoded questions when LLM unavailable

**Usage**:
```python
from oracle_engine.builder_node import BuilderNode

builder = BuilderNode()

# Generate questions
questions = builder.generate_questions(
    theme="slasher",
    difficulty=0.5,
    tone="creepy"
)

# Or generate full quiz
quiz = builder.generate_quiz(
    difficulty="intermediate",
    theme="monster"
)
```

**Output Structure**:
```json
[
  {
    "question": "When did Michael Myers first stalk Haddonfield's streets?",
    "choices": ["1975", "1978", "1980", "1983"],
    "correct_answer": "1978",
    "difficulty": 0.3,
    "tone": "creepy",
    "theme": "slasher"
  },
  ...4 more questions
]
```

### 2. Answer Evaluator (Evaluator Node)

**File**: `evaluator_node.py`

**Purpose**: Evaluates player answers and generates atmospheric Oracle feedback in character voice.

**Key Features**:
- Calculates score and percentage
- Assigns grade (S, A, B, C, D, F)
- Generates tone-appropriate Oracle reactions
- Provides detailed per-question feedback
- Recommends next action (advance, stay, retry, descend)
- Unlocks special lore on perfect scores
- Falls back to hardcoded feedback when LLM unavailable

**Usage**:
```python
from oracle_engine.evaluator_node import EvaluatorNode

evaluator = EvaluatorNode()

# Evaluate answers
result = evaluator.evaluate_answers(
    questions=questions,
    player_answers={
        "Question 1?": "Answer A",
        "Question 2?": "Answer B",
        ...
    },
    tone="creepy"
)
```

**Output Structure**:
```json
{
  "score": 4,
  "total": 5,
  "percentage": 80.0,
  "grade": "A",
  "verdict": "Your answers echo through empty corridors... 4 doors opened.",
  "detailed_feedback": [
    {
      "question": "...",
      "player_answer": "...",
      "correct_answer": "...",
      "is_correct": true,
      "comment": "The shadows approve..."
    }
  ],
  "oracle_reaction": "The Oracle's gaze lingers on you...",
  "next_action": "advance",
  "unlocked_lore": null
}
```

### 3. Prompt Templates

**Files**: 
- `prompts/question_generator_prompt.txt`
- `prompts/answer_evaluator_prompt.txt`

**Purpose**: Detailed instructions for the LLM to generate questions and feedback in the Horror Oracle's voice.

## Testing

Run the structure validation test:
```bash
cd oracle_engine
python test_structure.py
```

This test validates:
- Prompt file structure
- Builder node generates 5 valid questions
- Evaluator node scores and provides feedback
- All 6 tones work correctly
- Fallback logic when LLM unavailable

## Integration with Flask

### Example Flask Endpoint (Future)

```python
from flask import Blueprint, request, jsonify
from oracle_engine.builder_node import BuilderNode
from oracle_engine.evaluator_node import EvaluatorNode

oracle_bp = Blueprint('oracle', __name__)
builder = BuilderNode()
evaluator = EvaluatorNode()

@oracle_bp.route('/api/oracle/quiz/generate', methods=['POST'])
def generate_quiz():
    data = request.json
    quiz = builder.generate_quiz(
        difficulty=data.get('difficulty', 'intermediate'),
        theme=data.get('theme', 'general_horror')
    )
    return jsonify(quiz)

@oracle_bp.route('/api/oracle/quiz/evaluate', methods=['POST'])
def evaluate_quiz():
    data = request.json
    result = evaluator.evaluate_answers(
        questions=data['questions'],
        player_answers=data['answers'],
        tone=data.get('tone', 'creepy')
    )
    return jsonify(result)
```

## Configuration

The nodes use `backend/config.py` for configuration:

- `OPENAI_API_KEY`: Required for LLM-powered generation
- `LLM_MODEL`: Model to use (default: gpt-4)
- `LLM_TEMPERATURE`: Controls creativity (Builder: 0.8, Evaluator: 0.9)

Without API keys, both nodes automatically fall back to hardcoded questions/feedback.

## Atmospheric Tones

The Oracle speaks in 6 distinct voices:

1. **Creepy**: Unsettling, skin-crawling, intimate
2. **Mocking**: Taunting, condescending, darkly amused
3. **Ancient**: Archaic, timeless, biblical/mythic
4. **Whispered**: Secretive, conspiratorial, quiet
5. **Grim**: Dark, serious, no mercy, no levity
6. **Playful**: Fun but sinister, game-like, enjoying horror

## Difficulty Levels

- **0.1-0.3**: Beginner - Classic horror everyone knows
- **0.4-0.6**: Intermediate - Specific scenes, directors, lesser-known facts
- **0.7-0.9**: Advanced - Deep cuts, technical details, international horror
- **0.9-1.0**: Expert - Cult films, rare trivia, film theory

## Theme Categories

- `general_horror`: Mix of everything
- `slasher`: Killers, weapons, body counts
- `psychological`: Mind games, perception, madness
- `monster`: Creatures, transformations, designs
- `ghost`: Hauntings, spirits, supernatural
- `cosmic_horror`: Lovecraftian, existential dread
- `survival`: Final girls, escape tactics
- `lore`: Monster origins, mythology, backstories
- `movie`: Specific films, scenes, directors

## Next Steps

1. ✅ Builder Node: Complete
2. ✅ Evaluator Node: Complete
3. ✅ Prompt Templates: Complete
4. ✅ Testing: Complete
5. ⏳ Flask Integration: Ready (not implemented yet)
6. ⏳ Frontend Integration: Ready (not implemented yet)

## Files Created

```
oracle_engine/
├── builder_node.py                          # Question generator
├── evaluator_node.py                        # Answer evaluator
├── prompts/
│   ├── question_generator_prompt.txt        # LLM instructions for questions
│   └── answer_evaluator_prompt.txt          # LLM instructions for feedback
├── test_structure.py                        # Validation tests
└── README.md                                # This file
```

## Important Notes

- **No Flask changes needed yet** - These nodes are standalone and ready to integrate when needed
- **No frontend changes needed yet** - Current quiz system continues to work
- **Fallback logic ensures reliability** - Works even without LLM access
- **Fully tested** - All components validated with comprehensive test suite
- **Emoji-free for Windows compatibility** - Uses [OK], [WARN], [ERROR] markers instead

---

**Status**: ✅ **COMPLETE AND READY FOR INTEGRATION**

The Builder and Evaluator nodes are production-ready and can be integrated into the Flask backend when you're ready to add Oracle-powered adaptive quizzes.

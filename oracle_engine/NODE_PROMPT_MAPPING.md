# Oracle Engine - Node to Prompt Mapping

This document maps each LangGraph node to its corresponding prompt template.

## Node Files and Their Prompts

| Node File | Prompt Template | Purpose |
|-----------|----------------|---------|
| `builder_node.py` | `question_generator_prompt.txt` | Generates horror quiz questions tailored to user profile |
| `evaluator_node.py` | `answer_evaluator_prompt.txt` + `oracle_reactor_prompt.txt` | Evaluates answers and generates Oracle reactions |
| `reward_node.py` | `reward_generator_prompt.txt` | Generates rewards, achievements, and unlocks |
| `profile_node.py` | `profile_updater_prompt.txt` | Updates user profiles based on performance |
| `recommender_node.py` | `recommender_prompt.txt` | Recommends horror movies based on preferences |
| `lore_whisperer_node.py` | `lore_whisperer_prompt.txt` | Generates atmospheric lore and backstories |
| `fear_meter_node.py` | `fear_meter_prompt.txt` | Calculates and tracks user fear levels |

## The 8 Reusable Prompt Templates

1. **Question Generator Prompt** (`question_generator_prompt.txt`)
   - Used by: Builder Node
   - Purpose: Generate horror quiz questions with varying difficulty and themes

2. **Answer Evaluator Prompt** (`answer_evaluator_prompt.txt`)
   - Used by: Evaluator Node
   - Purpose: Evaluate correctness and provide detailed feedback

3. **Oracle Reactor Prompt** (`oracle_reactor_prompt.txt`)
   - Used by: Evaluator Node
   - Purpose: Generate atmospheric reactions from the Oracle

4. **Reward Generator Prompt** (`reward_generator_prompt.txt`)
   - Used by: Reward Node
   - Purpose: Create rewards, achievements, and unlock content

5. **Profile Updater Prompt** (`profile_updater_prompt.txt`)
   - Used by: Profile Node
   - Purpose: Analyze and update user preferences and performance

6. **Recommender Prompt** (`recommender_prompt.txt`)
   - Used by: Recommender Node
   - Purpose: Generate personalized movie recommendations

7. **Lore Whisperer Prompt** (`lore_whisperer_prompt.txt`)
   - Used by: Lore Whisperer Node
   - Purpose: Create atmospheric horror lore and narratives

8. **Fear Meter Prompt** (`fear_meter_prompt.txt`)
   - Used by: Fear Meter Node
   - Purpose: Calculate fear levels and psychological profiling

## Usage Example

```python
from oracle_engine.prompt_loader import load_prompt
from oracle_engine.builder_node import BuilderNode

# Initialize a node
builder = BuilderNode()

# Load its prompt template
prompt = builder.load_prompt()

# Or use the prompt loader directly
prompt = load_prompt("question_generator_prompt")
```

## Prompt Template Structure

Each prompt template file:
- Lives in `oracle_engine/prompts/`
- Has a `.txt` extension
- Will be filled with actual prompt content in subsequent sessions
- Can be loaded using the `PromptLoader` utility

## Next Steps

1. ✅ Create all 8 prompt template placeholder files
2. ✅ Create `prompt_loader.py` utility
3. ✅ Create/update all 7 node files
4. ✅ Wire up the structure
5. ⏳ Fill in actual prompt content (next session)
6. ⏳ Integrate with LangChain
7. ⏳ Connect nodes in LangGraph workflow


# Oracle Engine - Quick Reference Card

## 📁 Complete File Structure

```
oracle_engine/
├── 7 Node Files (All Present ✓)
│   ├── builder_node.py
│   ├── evaluator_node.py
│   ├── reward_node.py
│   ├── profile_node.py
│   ├── recommender_node.py
│   ├── lore_whisperer_node.py (NEW)
│   └── fear_meter_node.py (NEW)
│
├── prompts/ (9 Prompt Templates ✓)
│   ├── question_generator_prompt.txt (Has content)
│   ├── answer_evaluator_prompt.txt (Has content)
│   ├── oracle_reactor_prompt.txt (Empty - ready for content)
│   ├── reward_generator_prompt.txt (Empty - ready for content)
│   ├── profile_updater_prompt.txt (Empty - ready for content)
│   ├── recommender_prompt.txt (Empty - ready for content)
│   ├── lore_whisperer_prompt.txt (Empty - ready for content)
│   ├── fear_meter_prompt.txt (Empty - ready for content)
│   └── quiz_builder_prompt.txt (Existing)
│
├── Utilities
│   ├── prompt_loader.py (Prompt loading system)
│   ├── __init__.py (Package exports)
│   └── main.py (Main interface)
│
└── Documentation
    ├── README.md (Complete guide)
    ├── ARCHITECTURE.md (System architecture)
    ├── NODE_PROMPT_MAPPING.md (Node-to-prompt map)
    ├── SETUP_COMPLETE.md (Status summary)
    ├── QUICK_REFERENCE.md (This file)
    ├── verify_structure.py (Verification script)
    └── test_prompt_system.py (Test suite)
```

## 🎯 What's Ready to Use

### ✅ Fully Functional
- Prompt loader system (`prompt_loader.py`)
- All 7 node files created
- Package exports configured
- Verification tools working

### 📝 Needs Content (6 prompts)
1. `oracle_reactor_prompt.txt`
2. `reward_generator_prompt.txt`
3. `profile_updater_prompt.txt`
4. `recommender_prompt.txt`
5. `lore_whisperer_prompt.txt`
6. `fear_meter_prompt.txt`

## 🚀 Quick Start

### Load a Prompt
```python
from oracle_engine.prompt_loader import load_prompt
prompt = load_prompt("question_generator_prompt")
```

### Create a Node
```python
from oracle_engine import create_lore_node
lore = create_lore_node()
lore.load_prompt()
```

### Get All Prompts
```python
from oracle_engine import get_available_prompts
prompts = get_available_prompts()
```

## 🔍 Verify Setup
```bash
python oracle_engine/verify_structure.py
```

## 📊 Node → Prompt Mapping

| Node | Prompt(s) | Status |
|------|-----------|--------|
| Builder | question_generator_prompt.txt | ✓ Has content |
| Evaluator | answer_evaluator_prompt.txt<br>oracle_reactor_prompt.txt | ✓ Has content<br>○ Needs content |
| Reward | reward_generator_prompt.txt | ○ Needs content |
| Profile | profile_updater_prompt.txt | ○ Needs content |
| Recommender | recommender_prompt.txt | ○ Needs content |
| Lore Whisperer | lore_whisperer_prompt.txt | ○ Needs content |
| Fear Meter | fear_meter_prompt.txt | ○ Needs content |

## 📋 Next Session Checklist

Use this for the next 6 Cursor sessions (one prompt per session):

- [ ] **Session 1**: Fill in `oracle_reactor_prompt.txt`
- [ ] **Session 2**: Fill in `reward_generator_prompt.txt`
- [ ] **Session 3**: Fill in `profile_updater_prompt.txt`
- [ ] **Session 4**: Fill in `recommender_prompt.txt`
- [ ] **Session 5**: Fill in `lore_whisperer_prompt.txt`
- [ ] **Session 6**: Fill in `fear_meter_prompt.txt`

## 🎨 Prompt Template Format

Each prompt should follow this structure:

```
# [Node Name] Prompt
# Purpose: [What this prompt does]

## Context
[Explain the context this prompt operates in]

## Instructions
[Step-by-step instructions for the LLM]

## Input Format
[Expected input structure]

## Output Format
[Expected output structure]

## Examples
[1-2 examples showing input/output]

## Style Guidelines
[Tone, voice, atmospheric elements]
```

## 🛠️ Key Files

| File | Purpose | Size |
|------|---------|------|
| `prompt_loader.py` | Dynamic prompt loading | 3,791 bytes |
| `__init__.py` | Package exports | 1,651 bytes |
| `README.md` | Full documentation | 7,537 bytes |
| `ARCHITECTURE.md` | System architecture | Visual diagrams |
| `verify_structure.py` | Verification tool | Working ✓ |

## ⚡ What's Preserved

✅ All Flask endpoints in `horror.py`  
✅ All UI in `index.html` and `script-js-combined.js`  
✅ All database logic  
✅ Existing LangChain integration  
✅ Main interface functions  

## 🎯 Current Status

**✅ SETUP COMPLETE**  
**📝 READY FOR PROMPT CONTENT**  
**🚀 6 PROMPTS TO FILL**

---

*Last Updated: This Session*  
*Status: Structure Complete, Verified, Ready for Content*


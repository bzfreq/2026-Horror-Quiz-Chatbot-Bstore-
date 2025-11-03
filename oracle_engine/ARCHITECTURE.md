# Oracle Engine Architecture

## System Overview

The Horror Oracle Engine is a LangGraph-powered quiz system with 7 specialized nodes, each using reusable prompt templates for LangChain integration.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       HORROR ORACLE ENGINE                       │
│                      LangGraph Node System                       │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PROMPT LOADER SYSTEM                        │
│  • Dynamic loading from prompts/ directory                       │
│  • Automatic caching for performance                             │
│  • Hot reload capability                                         │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
        ┌──────────────────────┴──────────────────────┐
        │           prompts/ directory                 │
        ├──────────────────────────────────────────────┤
        │  • question_generator_prompt.txt    (Ready) │
        │  • answer_evaluator_prompt.txt      (Ready) │
        │  • oracle_reactor_prompt.txt        (Empty) │
        │  • reward_generator_prompt.txt      (Empty) │
        │  • profile_updater_prompt.txt       (Empty) │
        │  • recommender_prompt.txt           (Empty) │
        │  • lore_whisperer_prompt.txt        (Empty) │
        │  • fear_meter_prompt.txt            (Empty) │
        └──────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════
                         THE 7 NODES
═══════════════════════════════════════════════════════════════════

┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  BUILDER NODE   │      │ EVALUATOR NODE  │      │  REWARD NODE    │
│  (Question Gen) │      │ (Answer Eval)   │      │  (Rewards)      │
├─────────────────┤      ├─────────────────┤      ├─────────────────┤
│ • generate_quiz │      │ • evaluate_     │      │ • generate_     │
│ • generate_     │      │   answers       │      │   rewards       │
│   question      │      │ • generate_     │      │ • check_        │
│                 │      │   oracle_       │      │   achievements  │
│ Uses:           │      │   reaction      │      │ • unlock_       │
│ question_       │      │                 │      │   content       │
│ generator_      │      │ Uses:           │      │                 │
│ prompt.txt      │      │ answer_         │      │ Uses:           │
│                 │      │ evaluator_      │      │ reward_         │
│                 │      │ prompt.txt +    │      │ generator_      │
│                 │      │ oracle_reactor_ │      │ prompt.txt      │
│                 │      │ prompt.txt      │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘

┌─────────────────┐      ┌─────────────────┐
│  PROFILE NODE   │      │ RECOMMENDER     │
│  (Profile Mgmt) │      │ NODE (Movies)   │
├─────────────────┤      ├─────────────────┤
│ • update_       │      │ • recommend_    │
│   profile       │      │   movies        │
│ • analyze_      │      │ • explain_      │
│   preferences   │      │   recommendation│
│ • get_profile   │      │ • rank_movies   │
│                 │      │                 │
│ Uses:           │      │ Uses:           │
│ profile_        │      │ recommender_    │
│ updater_        │      │ prompt.txt      │
│ prompt.txt      │      │                 │
│                 │      │                 │
└─────────────────┘      └─────────────────┘

┌─────────────────┐      ┌─────────────────┐
│ LORE WHISPERER  │      │  FEAR METER     │
│ NODE (Lore)     │      │  NODE (Fear)    │
├─────────────────┤      ├─────────────────┤
│ • generate_lore │      │ • calculate_    │
│ • generate_     │      │   fear_level    │
│   backstory     │      │ • analyze_      │
│ • generate_     │      │   scare_        │
│   transition    │      │   tolerance     │
│                 │      │ • generate_     │
│ Uses:           │      │   fear_message  │
│ lore_whisperer_ │      │                 │
│ prompt.txt      │      │ Uses:           │
│                 │      │ fear_meter_     │
│ (NEW in this    │      │ prompt.txt      │
│  session)       │      │                 │
│                 │      │ (NEW in this    │
│                 │      │  session)       │
└─────────────────┘      └─────────────────┘

═══════════════════════════════════════════════════════════════════
                      DATA FLOW EXAMPLE
═══════════════════════════════════════════════════════════════════

User Request: "Start a horror quiz"
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. PROFILE NODE                                                  │
│    • Loads user preferences                                      │
│    • Determines difficulty level                                 │
│    • Checks quiz history                                         │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. FEAR METER NODE                                               │
│    • Calculates current fear level                               │
│    • Determines scare tolerance                                  │
│    • Suggests intensity                                          │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. LORE WHISPERER NODE                                           │
│    • Generates atmospheric intro                                 │
│    • Creates room description                                    │
│    • Sets the mood                                               │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. BUILDER NODE                                                  │
│    • Generates 5 quiz questions                                  │
│    • Tailored to user's level                                    │
│    • Themed based on preferences                                 │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
User answers questions...
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. EVALUATOR NODE                                                │
│    • Scores answers                                              │
│    • Generates feedback                                          │
│    • Creates Oracle reaction                                     │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. REWARD NODE                                                   │
│    • Calculates rewards                                          │
│    • Checks achievements                                         │
│    • Unlocks new content                                         │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. RECOMMENDER NODE                                              │
│    • Suggests horror movies                                      │
│    • Based on performance                                        │
│    • Personalized to taste                                       │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
Results displayed to user

═══════════════════════════════════════════════════════════════════
                   INTEGRATION WITH MAIN APP
═══════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│                        Main Flask App                            │
│                        (horror.py)                               │
├─────────────────────────────────────────────────────────────────┤
│  • HTTP endpoints                                                │
│  • User authentication                                           │
│  • Database queries                                              │
│  • Frontend serving                                              │
└─────────────────────────────────────────────────────────────────┘
                               │
                               │ calls
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Oracle Engine                               │
│                   (oracle_engine/)                               │
├─────────────────────────────────────────────────────────────────┤
│  • Quiz generation logic                                         │
│  • Answer evaluation                                             │
│  • User profiling                                                │
│  • Recommendations                                               │
└─────────────────────────────────────────────────────────────────┘
                               │
                               │ uses
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LangChain + OpenAI                            │
│              (via prompt templates)                              │
├─────────────────────────────────────────────────────────────────┤
│  • Natural language generation                                   │
│  • Question creation                                             │
│  • Atmospheric text                                              │
│  • Intelligent recommendations                                   │
└─────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════
                     DESIGN PRINCIPLES
═══════════════════════════════════════════════════════════════════

1. MODULARITY
   Each node has a single, clear responsibility
   Nodes can be developed and tested independently

2. REUSABILITY
   Prompt templates are separate from code
   Templates can be updated without changing code
   Multiple nodes can share prompt patterns

3. TESTABILITY
   Each node can be unit tested
   Prompt loading can be mocked
   Factory functions enable easy testing

4. EXTENSIBILITY
   Easy to add new nodes
   Easy to add new prompts
   Easy to modify existing behavior

5. BACKWARD COMPATIBILITY
   Main interface preserved
   Flask endpoints unchanged
   Database logic untouched

═══════════════════════════════════════════════════════════════════
                    FILE ORGANIZATION
═══════════════════════════════════════════════════════════════════

oracle_engine/
│
├── Core Node Files (7)
│   ├── builder_node.py              Question generation
│   ├── evaluator_node.py            Answer evaluation
│   ├── reward_node.py               Rewards and achievements
│   ├── profile_node.py              User profile management
│   ├── recommender_node.py          Movie recommendations
│   ├── lore_whisperer_node.py       Atmospheric storytelling
│   └── fear_meter_node.py           Fear level tracking
│
├── Prompt Templates (8)
│   └── prompts/
│       ├── question_generator_prompt.txt
│       ├── answer_evaluator_prompt.txt
│       ├── oracle_reactor_prompt.txt
│       ├── reward_generator_prompt.txt
│       ├── profile_updater_prompt.txt
│       ├── recommender_prompt.txt
│       ├── lore_whisperer_prompt.txt
│       └── fear_meter_prompt.txt
│
├── System Utilities (3)
│   ├── prompt_loader.py             Dynamic prompt loading
│   ├── __init__.py                  Package exports
│   └── main.py                      Main interface
│
├── Data Storage
│   └── data/
│       └── profiles/                User profiles
│
└── Documentation (5)
    ├── README.md                    Complete guide
    ├── NODE_PROMPT_MAPPING.md       Node mappings
    ├── ARCHITECTURE.md              This file
    ├── SETUP_COMPLETE.md            Status summary
    ├── verify_structure.py          Verification tool
    └── test_prompt_system.py        Test suite

═══════════════════════════════════════════════════════════════════

This architecture provides a solid foundation for building an intelligent,
adaptive horror quiz system powered by LangChain and LangGraph.


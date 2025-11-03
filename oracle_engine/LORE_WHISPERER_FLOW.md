# 🔮 Lore Whisperer Flow Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     HORROR ORACLE SYSTEM                        │
└─────────────────────────────────────────────────────────────────┘

                    ┌────────────────┐
                    │  Player takes  │
                    │      Quiz      │
                    └────────┬───────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  Quiz Scoring  │
                    │   (accuracy)   │
                    └────────┬───────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │       FEAR METER NODE                  │
        │  - Analyzes performance                │
        │  - Determines Oracle emotion           │
        │  - Calculates fear level               │
        │                                        │
        │  Output: oracle_state {                │
        │    "oracle_emotion": "pleased",        │
        │    "oracle_tone": "approving",         │
        │    "fear_level": 30,                   │
        │    "next_difficulty": "harder"         │
        │  }                                     │
        └────────────────┬───────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────┐
        │      LORE WHISPERER NODE               │
        │  ┌──────────────────────────────────┐  │
        │  │ INPUTS:                          │  │
        │  │  • player_profile (traits)       │  │
        │  │  • last_theme ("slasher")        │  │
        │  │  • emotion ("pleased")           │  │
        │  │  • performance ("excellent")     │  │
        │  └──────────────────────────────────┘  │
        │                                        │
        │  ┌──────────────────────────────────┐  │
        │  │ PROCESSING:                      │  │
        │  │  1. Calculate intensity          │  │
        │  │  2. Craft lore text              │  │
        │  │  3. Select fragment style        │  │
        │  │  4. Build atmosphere             │  │
        │  │  5. Define oracle voice          │  │
        │  │  6. Create narrative hooks       │  │
        │  └──────────────────────────────────┘  │
        │                                        │
        │  ┌──────────────────────────────────┐  │
        │  │ OUTPUTS: (JSON)                  │  │
        │  │  • lore_fragment {text, style}   │  │
        │  │  • atmosphere {mood, visuals}    │  │
        │  │  • oracle_voice {tone, volume}   │  │
        │  │  • narrative_hooks               │  │
        │  │  • metadata                      │  │
        │  └──────────────────────────────────┘  │
        └────────────────┬───────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────┐
        │         FRONTEND DISPLAY               │
        │  ┌──────────────────────────────────┐  │
        │  │  📜 Display lore text            │  │
        │  │  🌑 Apply atmosphere effects     │  │
        │  │  🎭 Style Oracle's voice         │  │
        │  │  🔊 Play ambient sound           │  │
        │  │  ✨ Show visual hints            │  │
        │  └──────────────────────────────────┘  │
        └────────────────┬───────────────────────┘
                         │
                         ▼
                    ┌────────────────┐
                    │   Next Quiz    │
                    │    Chamber     │
                    └────────────────┘
```

---

## Data Flow Example

### Scenario: Player Aces a Slasher Quiz

```
INPUT:
├── player_profile = {
│     "name": "BloodSeeker",
│     "bravery": 75,
│     "lore_knowledge": 85,
│     "fear_level": 30,
│     "level": 3
│   }
├── last_theme = "slasher"
├── emotion = "pleased" (from Fear Meter)
└── performance = "excellent"

                    ↓ Processing ↓

LORE WHISPERER LOGIC:
├── Calculate Intensity:
│   └── emotion_intensity_map["pleased"] = 0.3
│   └── fear_modifier = 30/100 = 0.3
│   └── intensity = (0.3 × 0.7) + (0.3 × 0.3) = 0.3
│
├── Craft Lore Text:
│   └── Select from "pleased" templates
│   └── Result: "Even the shadows bow to those who know their names."
│
├── Select Fragment Style:
│   └── emotion = "pleased" → style = "dark_wisdom"
│
├── Build Atmosphere:
│   └── mood = "mysterious" (from mood_map)
│   └── visual_hints = ["decaying_walls", "flickering_candles"]
│   └── ambient_sound = "dripping_water"
│   └── intensity_level = "low" (intensity 0.3)
│
├── Define Oracle Voice:
│   └── tone = "pleased"
│   └── intimacy_level = "approving"
│   └── volume = "normal"
│
└── Create Narrative Hooks:
    └── references_last_theme = true (70% chance)
    └── foreshadows_next = false (40% chance)
    └── personal_observation = "The Oracle marks your progress, BloodSeeker."
    └── hints_at_rewards = true (bravery > 70 && performance = excellent)

                    ↓ Output ↓

OUTPUT JSON:
{
  "lore_fragment": {
    "text": "Even the shadows bow to those who know their names.",
    "style": "dark_wisdom",
    "intensity": 0.3
  },
  "atmosphere": {
    "mood": "mysterious",
    "visual_hints": ["decaying_walls", "flickering_candles"],
    "ambient_sound": "dripping_water",
    "intensity_level": "low"
  },
  "oracle_voice": {
    "tone": "pleased",
    "emotion": "pleased",
    "intimacy_level": "approving",
    "volume": "normal"
  },
  "narrative_hooks": {
    "references_last_theme": true,
    "foreshadows_next": false,
    "personal_observation": "The Oracle marks your progress, BloodSeeker.",
    "hints_at_rewards": true
  },
  "metadata": {
    "fragment_type": "transition",
    "trigger": "quiz_completion",
    "duration_seconds": 4,
    "player_level": 3
  }
}

                    ↓ Frontend ↓

DISPLAY:
┌─────────────────────────────────────────────────┐
│              🌑 MYSTERIOUS CHAMBER               │
│                                                 │
│  [decaying_walls]    [flickering_candles]      │
│                                                 │
│          🔊 dripping_water (ambient)            │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │   "Even the shadows bow to those who      │  │
│  │        know their names."                 │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  🎭 The Oracle speaks approvingly...            │
│                                                 │
│  💬 "The Oracle marks your progress,            │
│      BloodSeeker."                              │
│                                                 │
│  ✨ Rewards may await...                        │
│                                                 │
│  [Duration: 4 seconds] → [Next Chamber]        │
└─────────────────────────────────────────────────┘
```

---

## Emotion → Style Mapping

```
Oracle Emotion         Fragment Style           Intensity   Volume
─────────────────      ──────────────────       ─────────   ────────────
pleased           →    dark_wisdom              0.3         normal
amused            →    mocking_observation      0.5         normal
mocking           →    mocking_observation      0.7         normal
disappointed      →    cryptic_prophecy         0.6         normal
wrathful          →    ancient_warning          0.9         thunderous
cruel             →    ancient_warning          0.85        thunderous
indifferent       →    cryptic_prophecy         0.4         whisper

                       ↓ If intensity > 0.8 ↓

High Intensity    →    eldritch_whisper         0.8+        thunderous
```

---

## Frontend Integration Points

### 1. Display Lore Text
```javascript
const loreText = loreData.lore_fragment.text;
const style = loreData.lore_fragment.style;

displayLoreOverlay(loreText, style);
```

### 2. Apply Atmosphere
```javascript
const mood = loreData.atmosphere.mood;
const visuals = loreData.atmosphere.visual_hints;
const sound = loreData.atmosphere.ambient_sound;

setAtmosphere(mood, visuals);
playAmbientSound(sound);
```

### 3. Oracle Voice Styling
```javascript
const tone = loreData.oracle_voice.tone;
const volume = loreData.oracle_voice.volume;
const intimacy = loreData.oracle_voice.intimacy_level;

styleOracleVoice(tone, volume, intimacy);
```

### 4. Narrative Hooks
```javascript
const hooks = loreData.narrative_hooks;

if (hooks.personal_observation) {
    showPersonalMessage(hooks.personal_observation);
}

if (hooks.hints_at_rewards) {
    showRewardTeaser();
}

if (hooks.foreshadows_next) {
    showNextChamberHint();
}
```

### 5. Timing
```javascript
const duration = loreData.metadata.duration_seconds;

setTimeout(() => {
    transitionToNextChamber();
}, duration * 1000);
```

---

## Complete Integration Code

```python
from oracle_engine.fear_meter_node import FearMeterNode
from oracle_engine.lore_whisperer_node import LoreWhispererNode

def handle_quiz_completion(user_id, quiz, answers, player_profile):
    """
    Complete flow: Quiz → Evaluation → Lore Generation → Display
    """
    
    # 1. Evaluate quiz performance
    fear_meter = FearMeterNode()
    
    # Calculate accuracy
    score = sum(1 for q in quiz["questions"] 
                if answers.get(q["question"]) == q["answer"])
    accuracy = score / len(quiz["questions"])
    
    # Translate to Oracle state
    oracle_state = fear_meter.translate_to_oracle_state(
        accuracy=accuracy,
        previous_tone=player_profile.get("last_oracle_tone", "neutral"),
        player_profile=player_profile
    )
    
    # Determine performance category
    if accuracy >= 0.8:
        performance = "excellent"
    elif accuracy >= 0.6:
        performance = "good"
    elif accuracy >= 0.4:
        performance = "average"
    else:
        performance = "poor"
    
    # 2. Generate lore fragment
    lore_node = LoreWhispererNode()
    lore = lore_node.whisper_between_chambers(
        player_profile=player_profile,
        last_theme=quiz.get("theme", "horror"),
        emotion=oracle_state["oracle_emotion"],
        performance=performance
    )
    
    # 3. Update player profile
    player_profile["fear_level"] = oracle_state["player_state"]["fear_level"]
    player_profile["last_oracle_tone"] = oracle_state["next_tone"]
    
    # 4. Return complete result for frontend
    return {
        "quiz_results": {
            "score": score,
            "total": len(quiz["questions"]),
            "accuracy": accuracy,
            "performance": performance
        },
        "oracle_state": oracle_state,
        "lore_fragment": lore,
        "updated_profile": player_profile
    }
```

---

## State Persistence

```
Player Session State:
├── player_profile {
│     "name": "BloodSeeker",
│     "bravery": 75,
│     "lore_knowledge": 85,
│     "fear_level": 30,     ← Updated by Fear Meter
│     "level": 3,
│     "last_oracle_tone": "pleased"  ← Used for next evaluation
│   }
│
└── Quiz History [
      {
        "theme": "slasher",
        "score": 8/10,
        "oracle_emotion": "pleased",
        "lore_shown": "Even the shadows bow..."
      },
      ...
    ]
```

---

**The Oracle's voice echoes through the chambers...**


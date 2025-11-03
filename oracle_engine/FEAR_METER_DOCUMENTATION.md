# Fear Meter Node - Documentation

## Overview
The Fear Meter Node translates quiz performance (accuracy scores) into the Horror Oracle's emotional and tonal state for the next interaction. It provides rich atmospheric narrative elements and behavioral modifications based on player performance.

## Purpose
Transform raw quiz scores into a dynamic, emotional Oracle experience that responds intelligently to player performance, creating an immersive horror quiz atmosphere.

---

## Core Function: `translate_to_oracle_state()`

### Inputs
```python
def translate_to_oracle_state(
    accuracy: float,           # Quiz accuracy (0.0 - 1.0)
    previous_tone: str,        # Previous Oracle tone
    player_profile: dict       # Player data
) -> dict:
```

#### Player Profile Structure
```python
{
    "name": "PlayerName",
    "bravery": 50,              # 0-100
    "lore_knowledge": 50,       # 0-100
    "logic": 50,                # 0-100
    "fear_level": 50            # 0-100 (optional)
}
```

### Outputs (JSON)
```python
{
    "oracle_tone": str,              # Current emotional tone
    "oracle_emotion": str,           # Specific emotion
    "intensity": float,              # 0.0 - 1.0
    "next_tone": str,                # Suggested next tone
    "fear_shift": float,             # -1.0 to +1.0
    "atmospheric_message": str,      # Oracle's reaction
    
    "player_state": {
        "confidence": str,           # confident/shaken/terrified/neutral
        "performance_trend": str,    # improving/declining/stable
        "fear_level": int            # Updated 0-100
    },
    
    "oracle_behavior": {
        "difficulty_adjustment": str,  # reward/maintain/punish
        "reveal_lore": bool,          # Grant lore access
        "mock_intensity": str,        # low/medium/high
        "rewards_granted": list       # List of rewards
    },
    
    "narrative_context": {
        "chamber_atmosphere": str,    # oppressive/tense/watchful/calm
        "oracle_stance": str,         # Physical presence description
        "transition_text": str        # Bridge to next phase
    }
}
```

---

## Oracle Tone Scale

### Performance-Based Tones

| Accuracy | Tone | Emotion | Intensity | Fear Shift | Difficulty |
|----------|------|---------|-----------|------------|------------|
| 90%+ | **Reverent** | Impressed | 0.85 | -0.20 | Reward |
| 70-89% | **Ancient** | Respectful | 0.60 | -0.10 | Maintain |
| 50-69% | **Neutral** | Observing | 0.50 | 0.00 | Maintain |
| 30-49% | **Disappointed** | Condescending | 0.70 | +0.15 | Maintain |
| <30% | **Mocking** | Amused | 0.90 | +0.30 | Punish |

### Tone Descriptions

**Reverent** (High Performance)
- Oracle shows respect and admiration
- Player has demonstrated mastery
- Rewards: Lore fragments, Oracle blessings
- Example: *"You honor the ancient knowledge..."*

**Ancient** (Good Performance)  
- Oracle acknowledges understanding
- Solemn, timeless approval
- Rewards: Some lore access
- Example: *"The old ways are not lost on you..."*

**Neutral** (Average Performance)
- Oracle watches with detachment
- Neither impressed nor disappointed
- No special treatment
- Example: *"Proceed..."*

**Disappointed** (Poor Performance)
- Oracle shows letdown and disdain
- Player hasn't met expectations
- Penalties: No rewards, mockery begins
- Example: *"Expected more..."*

**Mocking** (Very Poor Performance)
- Oracle finds entertainment in failure
- Maximum intensity and cruelty
- Penalties: Harder questions, no lore
- Example: *"Pathetic mortal..."*

---

## Tone Transitions

The Oracle's tone flows naturally between states:

```
Reverent → Ancient, Impressed, Neutral
Mocking → Creepy, Disappointed, Amused
Ancient → Reverent, Neutral, Creepy
Creepy → Mocking, Ancient, Disappointed
Neutral → (Can shift to any based on performance)
```

Transitions are influenced by:
1. Current accuracy
2. Previous tone
3. Performance trends

---

## Behavioral Modifications

### Difficulty Adjustments

**Reward** (90%+ accuracy)
- Slightly easier questions
- More hints available
- Bonus lore unlocked
- Positive reinforcement

**Maintain** (30-89% accuracy)
- Keep current difficulty
- Standard challenge level
- No special adjustments

**Punish** (<30% accuracy)
- Harder questions
- Obscure trivia
- Time pressure added
- Oracle mockery intensifies

### Lore Revelation
- **Unlocked**: 70%+ accuracy
- **Locked**: <70% accuracy
- Special lore for 90%+ (Oracle blessings)

### Rewards System
```python
# 90%+ accuracy
rewards_granted = ["lore_fragment", "oracle_blessing"]

# 70-89% accuracy  
rewards_granted = ["lore_fragment"]

# <70% accuracy
rewards_granted = []  # None
```

---

## Atmospheric Elements

### Chamber Atmospheres
- **Oppressive** (intensity > 0.8): Heavy, threatening presence
- **Tense** (intensity > 0.6): Charged, anticipatory
- **Watchful** (intensity > 0.4): Observant, neutral
- **Calm** (intensity ≤ 0.4): Peaceful, accepting

### Oracle Physical Stances

**Reverent Tone:**
> "The Oracle rises from its throne, robes flowing like shadow and light intertwined"

**Ancient Tone:**
> "The Oracle sits motionless, eyes older than time itself watching patiently"

**Neutral Tone:**
> "The Oracle remains still, an enigmatic presence in the darkness"

**Disappointed Tone:**
> "The Oracle's form seems to dim, shadows deepening around its disappointment"

**Mocking Tone:**
> "The Oracle leans forward, eyes gleaming with dark amusement and malice"

*Enhanced with intensity modifiers like "power radiating from every gesture"*

---

## Fear Level Dynamics

### Fear Shift Calculation
```python
current_fear = player_profile.get("fear_level", 50)
new_fear_level = max(0, min(100, current_fear + (fear_shift * 100)))
```

### Fear Impact
- **High Performance**: Reduces fear (-20 to -10 points)
- **Average Performance**: Stable (±5 points)
- **Poor Performance**: Increases fear (+15 to +30 points)

### Player Confidence States
- **Confident**: Fear level decreasing, good performance
- **Neutral**: Stable fear level, average performance
- **Shaken**: Fear increasing, performance declining
- **Terrified**: High fear, very poor performance

---

## Integration Example

```python
from oracle_engine.fear_meter_node import FearMeterNode

# Initialize Fear Meter
fear_meter = FearMeterNode()

# Player profile
player = {
    "name": "DarkSeeker",
    "bravery": 65,
    "lore_knowledge": 70,
    "logic": 75,
    "fear_level": 50
}

# After quiz evaluation
quiz_accuracy = 0.85  # 85% correct

# Translate to Oracle state
oracle_state = fear_meter.translate_to_oracle_state(
    accuracy=quiz_accuracy,
    previous_tone="neutral",
    player_profile=player
)

# Use the results
print(oracle_state["atmospheric_message"])
# Output: "'Acceptable,' whispers the ancient voice. 'Continue your journey.'"

print(f"Fear Level: {oracle_state['player_state']['fear_level']}")
# Output: Fear Level: 40

print(f"Difficulty: {oracle_state['oracle_behavior']['difficulty_adjustment']}")
# Output: Difficulty: maintain
```

---

## Testing

Run the comprehensive test suite:
```bash
python oracle_engine/test_fear_meter.py
```

This tests:
1. All accuracy scenarios (100%, 85%, 60%, 35%, 15%)
2. Oracle tone transitions
3. Fear level adjustments
4. Behavioral modifications
5. Atmospheric narrative generation

---

## Design Philosophy

The Fear Meter isn't just calculating numbers—it's **breathing life into an ancient, powerful entity** that reacts emotionally to mortal attempts to understand the horror genre.

### Key Principles:
1. **Dynamic Response**: Oracle changes based on performance
2. **Emotional Depth**: Rich atmospheric descriptions
3. **Natural Progression**: Smooth tone transitions
4. **Immersive Narrative**: Player feels the Oracle's presence
5. **Balanced Difficulty**: Rewards mastery, punishes failure

---

## Future Enhancements

Potential additions (not yet implemented):
- LangChain integration for AI-generated responses
- Historical performance tracking
- Personality-based tone adjustments
- Multi-factor fear calculation (beyond just accuracy)
- Achievement system integration

---

## Files

- **Node**: `oracle_engine/fear_meter_node.py`
- **Prompt**: `oracle_engine/prompts/fear_meter_prompt.txt`
- **Test**: `oracle_engine/test_fear_meter.py`
- **Integration**: `oracle_engine/main.py` (updated `evaluate_and_progress()`)

---

## Version
**v0.2.0** - Initial Fear Meter implementation with full JSON output structure


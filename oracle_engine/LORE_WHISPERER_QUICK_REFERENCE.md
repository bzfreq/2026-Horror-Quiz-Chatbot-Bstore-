# Lore Whisperer - Quick Reference

## Purpose
Generate short, poetic horror fragments between quiz chambers for immersion.

---

## Quick Start

```python
from oracle_engine.lore_whisperer_node import LoreWhispererNode

lore_node = LoreWhispererNode()

# Generate lore between chambers
lore = lore_node.whisper_between_chambers(
    player_profile={
        "name": "DarkSeeker",
        "bravery": 75,
        "lore_knowledge": 85,
        "fear_level": 30,
        "level": 3
    },
    last_theme="slasher",
    emotion="pleased",
    performance="excellent"
)

# Access the lore text
print(lore["lore_fragment"]["text"])
```

---

## JSON Output Structure (Quick View)

```json
{
  "lore_fragment": {
    "text": "Even the shadows bow...",
    "style": "dark_wisdom",
    "intensity": 0.75
  },
  "atmosphere": {
    "mood": "mysterious",
    "visual_hints": ["blood_moon", "shadows"],
    "ambient_sound": "whispers",
    "intensity_level": "medium"
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
    "personal_observation": "The Oracle marks...",
    "hints_at_rewards": true
  },
  "metadata": {
    "fragment_type": "transition",
    "trigger": "quiz_completion",
    "duration_seconds": 4,
    "player_level": 3
  }
}
```

---

## Input Parameters

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `player_profile.name` | string | Any | Player's name |
| `player_profile.bravery` | int | 0-100 | Courage level |
| `player_profile.lore_knowledge` | int | 0-100 | Horror knowledge |
| `player_profile.fear_level` | int | 0-100 | Current fear |
| `player_profile.level` | int | 1+ | Player level |
| `last_theme` | string | slasher, occult, supernatural, psychological, body_horror, cosmic | Last quiz theme |
| `emotion` | string | pleased, amused, mocking, disappointed, wrathful, cruel, indifferent | Oracle's emotion |
| `performance` | string | excellent, good, average, poor | Quiz performance |

---

## Emotion → Output Quick Map

| Emotion | Style | Intensity | Example |
|---------|-------|-----------|---------|
| pleased | dark_wisdom | 0.3 | "Knowledge gleams in darkness..." |
| amused | mocking_observation | 0.5 | "You dance well, mortal." |
| mocking | mocking_observation | 0.7 | "Did you think it so easy?" |
| disappointed | cryptic_prophecy | 0.6 | "Mediocrity echoes hollow..." |
| wrathful | ancient_warning | 0.9 | "FOOL! The spirits howl!" |
| cruel | eldritch_whisper | 0.85 | "Your fear is exquisite..." |
| indifferent | cryptic_prophecy | 0.4 | "The void watches. Waits." |

---

## Atmosphere Fields

**Moods**: ominous, dread, eerie, malevolent, mysterious, suffocating

**Visual Hints**: flickering_candles, shadow_figures, blood_moon, cracked_mirrors, writhing_shadows, spectral_mist, ancient_runes, decaying_walls, crimson_light

**Ambient Sounds**: distant_whispers, chains_rattling, mournful_wind, dripping_water, heartbeat_echo, screaming_silence

**Intensity Levels**: low, medium, high

---

## Common Usage Patterns

### After Quiz Completion
```python
lore = lore_node.whisper_between_chambers(
    player_profile=player_data,
    last_theme=current_quiz_theme,
    emotion=oracle_emotion_from_fear_meter,
    performance=calculate_performance(score, total)
)
```

### Movie Backstory
```python
backstory = lore_node.generate_backstory({
    "title": "Halloween",
    "year": 1978
})
```

### Chamber Transition
```python
transition = lore_node.generate_transition(
    from_room="The Slasher's Den",
    to_room="The Occult Chamber",
    performance="excellent",
    player_profile=player_data
)
```

---

## Testing

```bash
cd c:\31000
python oracle_engine\test_lore_whisperer.py
```

---

## Integration with Fear Meter

```python
from oracle_engine.fear_meter_node import FearMeterNode
from oracle_engine.lore_whisperer_node import LoreWhispererNode

fear_meter = FearMeterNode()
lore_node = LoreWhispererNode()

# Get Oracle's emotional state
oracle_state = fear_meter.translate_to_oracle_state(
    accuracy=0.8,
    previous_tone="neutral",
    player_profile=player_data
)

# Generate lore based on that emotion
lore = lore_node.whisper_between_chambers(
    player_profile=player_data,
    last_theme="slasher",
    emotion=oracle_state["oracle_emotion"],
    performance="good"
)
```

---

## Frontend Display Pattern

```javascript
function displayLoreFragment(lore) {
  // Show lore text
  $('#lore-text').text(lore.lore_fragment.text);
  
  // Apply atmosphere
  $('body').attr('data-mood', lore.atmosphere.mood);
  
  // Show visual effects
  lore.atmosphere.visual_hints.forEach(hint => {
    applyVisualEffect(hint);
  });
  
  // Play sound
  playSound(lore.atmosphere.ambient_sound);
  
  // Auto-hide after duration
  setTimeout(() => {
    hideLore();
  }, lore.metadata.duration_seconds * 1000);
}
```

---

## Performance Tips

- Generation is <10ms (rule-based)
- No LLM calls in current implementation
- Fully deterministic for testing
- Can generate 100+ lore fragments/second
- Safe for real-time gameplay

---

## Files

```
oracle_engine/
├── lore_whisperer_node.py                 # Implementation
├── test_lore_whisperer.py                 # Tests
├── LORE_WHISPERER_DOCUMENTATION.md        # Full docs
├── LORE_WHISPERER_QUICK_REFERENCE.md      # This file
└── prompts/
    └── lore_whisperer_prompt.txt          # Future LLM prompt
```

---

## Troubleshooting

**Issue**: Lore text is too long  
**Fix**: Check duration_seconds, should be 3-8

**Issue**: Emotion not recognized  
**Fix**: Use one of: pleased, amused, mocking, disappointed, wrathful, cruel, indifferent

**Issue**: Theme not referenced  
**Fix**: Set `references_last_theme=True` in output (70% chance by default)

**Issue**: No personalization  
**Fix**: Ensure player_profile includes "name" field

---

*For full documentation, see LORE_WHISPERER_DOCUMENTATION.md*

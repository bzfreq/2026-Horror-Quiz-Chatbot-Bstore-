# Lore Whisperer Node Documentation

## Purpose
The **Lore Whisperer Node** generates short, poetic fragments of horror lore between quiz chambers. These fragments add immersion — like the Oracle whispering cryptic prophecies or recounting old myths.

---

## JSON Output Structure

### Complete Output Format

```json
{
  "lore_fragment": {
    "text": "Even the shadows bow to those who know their names.",
    "style": "dark_wisdom",
    "intensity": 0.75
  },
  "atmosphere": {
    "mood": "mysterious",
    "visual_hints": ["blood_moon", "shadow_figures"],
    "ambient_sound": "screaming_silence",
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
    "personal_observation": "The Oracle marks your progress, Seeker.",
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

## Field Descriptions

### 1. `lore_fragment`
The core poetic text that the Oracle speaks.

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | The actual lore text the Oracle whispers (30-80 characters) |
| `style` | string | Style of the fragment: `cryptic_prophecy`, `ancient_warning`, `mocking_observation`, `dark_wisdom`, `eldritch_whisper` |
| `intensity` | float | 0.0-1.0, how intense/dramatic the fragment is |

**Example texts by style:**
- **cryptic_prophecy**: "The void watches. The void waits."
- **ancient_warning**: "FOOL! The spirits howl at your ignorance!"
- **mocking_observation**: "Did you think darkness would yield so easily?"
- **dark_wisdom**: "Even the shadows bow to those who know their names."
- **eldritch_whisper**: "Your fear-scent grows sweeter..."

---

### 2. `atmosphere`
Describes the environmental/sensory context of the lore fragment.

| Field | Type | Description |
|-------|------|-------------|
| `mood` | string | Overall emotional atmosphere: `ominous`, `dread`, `eerie`, `malevolent`, `mysterious`, `suffocating` |
| `visual_hints` | array[string] | 2-3 visual elements for the UI: `flickering_candles`, `shadow_figures`, `blood_moon`, `cracked_mirrors`, `writhing_shadows`, `spectral_mist`, `ancient_runes`, `decaying_walls`, `crimson_light` |
| `ambient_sound` | string | Background sound effect: `distant_whispers`, `chains_rattling`, `mournful_wind`, `dripping_water`, `heartbeat_echo`, `screaming_silence` |
| `intensity_level` | string | `low`, `medium`, or `high` - guides visual/audio intensity |

---

### 3. `oracle_voice`
Defines how the Oracle delivers the lore fragment.

| Field | Type | Description |
|-------|------|-------------|
| `tone` | string | Oracle's current tone: `pleased`, `amused`, `mocking`, `disappointed`, `wrathful`, `cruel`, `indifferent` |
| `emotion` | string | Oracle's emotion (usually same as tone) |
| `intimacy_level` | string | How personal/distant the Oracle feels: `approving`, `playful`, `distant`, `cold`, `overwhelming`, `intimate`, `detached`, `neutral` |
| `volume` | string | Delivery volume: `whisper`, `normal`, `thunderous` |

**Intimacy Level Guide:**
- **approving** - Oracle is pleased, closer to player
- **playful** - Oracle is entertained, toying with player
- **distant** - Oracle is aloof, superior
- **cold** - Oracle is disappointed, withdrawing
- **overwhelming** - Oracle's presence is crushing
- **intimate** - Oracle is dangerously close, personal
- **detached** - Oracle doesn't care

---

### 4. `narrative_hooks`
Connects the lore to the player's journey and creates continuity.

| Field | Type | Description |
|-------|------|-------------|
| `references_last_theme` | boolean | Does the fragment mention the previous quiz theme? |
| `foreshadows_next` | boolean | Does it hint at what's coming? |
| `personal_observation` | string | A direct comment about the player (e.g., "Seeker trembles, yet persists...") |
| `hints_at_rewards` | boolean | Does it suggest rewards/recognition are coming? |

---

### 5. `metadata`
Technical information for the system.

| Field | Type | Description |
|-------|------|-------------|
| `fragment_type` | string | Type of fragment: `transition`, `intro`, `victory`, `defeat` |
| `trigger` | string | What triggered this fragment: `quiz_completion`, `level_up`, `chamber_enter` |
| `duration_seconds` | integer | Estimated reading time (3-8 seconds) |
| `player_level` | integer | Player's current level |

---

## Input Parameters

### Method: `whisper_between_chambers()`

```python
lore_node.whisper_between_chambers(
    player_profile={
        "name": "DarkSeeker",
        "bravery": 75,
        "lore_knowledge": 85,
        "fear_level": 30,
        "level": 3,
        "relics": ["Jason's Mask"]
    },
    last_theme="slasher",
    emotion="pleased",
    performance="excellent"
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `player_profile` | dict | Player's traits, level, and relics |
| `last_theme` | string | Theme of the last quiz: `slasher`, `occult`, `supernatural`, `psychological`, `body_horror`, etc. |
| `emotion` | string | Oracle's current emotion from Reactor/Fear Meter node |
| `performance` | string | Player's performance: `excellent`, `good`, `average`, `poor` |

### Player Profile Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Player's chosen name |
| `bravery` | integer | 0-100, affects narrative tone |
| `lore_knowledge` | integer | 0-100, how knowledgeable they are |
| `fear_level` | integer | 0-100, current fear state |
| `level` | integer | Player's current level |
| `relics` | array[string] | (Optional) Collected horror relics |

---

## Usage Examples

### Example 1: After Perfect Quiz Performance

```python
from oracle_engine.lore_whisperer_node import LoreWhispererNode

lore_node = LoreWhispererNode()

lore = lore_node.whisper_between_chambers(
    player_profile={
        "name": "BloodSeeker",
        "bravery": 85,
        "lore_knowledge": 90,
        "fear_level": 25,
        "level": 5
    },
    last_theme="slasher",
    emotion="pleased",
    performance="excellent"
)

# Display the lore text
print(lore["lore_fragment"]["text"])
# Output: "Even the shadows bow to those who know their names."

# Check if rewards are hinted
if lore["narrative_hooks"]["hints_at_rewards"]:
    print("Oracle suggests rewards are coming!")
```

### Example 2: After Poor Quiz Performance

```python
lore = lore_node.whisper_between_chambers(
    player_profile={
        "name": "NoviceSeeker",
        "bravery": 40,
        "lore_knowledge": 35,
        "fear_level": 75,
        "level": 1
    },
    last_theme="occult",
    emotion="mocking",
    performance="poor"
)

# The Oracle will mock the player
print(lore["lore_fragment"]["text"])
# Output: "Knowledge slips through trembling fingers like sand."

# Higher intensity and malevolent atmosphere
print(f"Intensity: {lore['lore_fragment']['intensity']}")  # ~0.7
print(f"Mood: {lore['atmosphere']['mood']}")  # "malevolent"
```

### Example 3: Oracle's Wrath

```python
lore = lore_node.whisper_between_chambers(
    player_profile={
        "name": "FoolishMortal",
        "bravery": 30,
        "lore_knowledge": 25,
        "fear_level": 90,
        "level": 2
    },
    last_theme="supernatural",
    emotion="wrathful",
    performance="poor"
)

# Oracle is furious
print(lore["lore_fragment"]["text"])
# Output: "FOOL! The supernatural spirits howl at your ignorance!"

print(f"Style: {lore['lore_fragment']['style']}")  # "ancient_warning"
print(f"Volume: {lore['oracle_voice']['volume']}")  # "thunderous"
print(f"Intimacy: {lore['oracle_voice']['intimacy_level']}")  # "overwhelming"
```

---

## Integration with Frontend

### JavaScript Integration Example

```javascript
async function displayLoreFragment(playerId, lastTheme, emotion, performance) {
  const response = await fetch('/api/oracle/lore-whisper', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      player_id: playerId,
      last_theme: lastTheme,
      emotion: emotion,
      performance: performance
    })
  });
  
  const lore = await response.json();
  
  // Display the lore text with fade-in
  document.getElementById('lore-text').textContent = lore.lore_fragment.text;
  
  // Apply atmosphere
  setAtmosphere(lore.atmosphere.mood, lore.atmosphere.intensity_level);
  
  // Show visual hints
  displayVisualHints(lore.atmosphere.visual_hints);
  
  // Play ambient sound
  playAmbientSound(lore.atmosphere.ambient_sound);
  
  // Auto-advance after duration
  setTimeout(() => {
    fadeOutLore();
  }, lore.metadata.duration_seconds * 1000);
}
```

### Atmosphere Mapping (CSS/Effects)

```javascript
const ATMOSPHERE_EFFECTS = {
  'ominous': { bg: '#1a0a0a', glow: 'red' },
  'dread': { bg: '#0a0a1a', glow: 'purple' },
  'eerie': { bg: '#0f1a0f', glow: 'green' },
  'malevolent': { bg: '#1a0000', glow: 'crimson' },
  'mysterious': { bg: '#0a0a14', glow: 'blue' },
  'suffocating': { bg: '#000000', glow: 'gray' }
};
```

---

## Emotion → Lore Mapping

| Oracle Emotion | Lore Style | Typical Intensity | Example Text |
|----------------|------------|-------------------|--------------|
| pleased | dark_wisdom | 0.3 | "Knowledge gleams in the darkness..." |
| amused | mocking_observation | 0.5 | "You dance well, little mortal." |
| mocking | mocking_observation | 0.7 | "Did you think it would be so easy?" |
| disappointed | cryptic_prophecy | 0.6 | "Mediocrity echoes hollow..." |
| wrathful | ancient_warning | 0.9 | "FOOL! The spirits howl!" |
| cruel | eldritch_whisper | 0.85 | "Your fear is exquisite..." |
| indifferent | cryptic_prophecy | 0.4 | "The void watches. The void waits." |

---

## Additional Methods

### `generate_backstory(movie_data)`

Generates horror-themed backstory for a specific movie.

```python
backstory = lore_node.generate_backstory({
    "title": "The Exorcist",
    "year": 1973
})
# Output: "In 1973, The Exorcist emerged from the void—a curse captured on celluloid."
```

### `generate_transition(from_room, to_room, performance, player_profile)`

Generates transition text between chambers.

```python
transition = lore_node.generate_transition(
    from_room="The Slasher's Den",
    to_room="The Occult Chamber",
    performance="excellent",
    player_profile={"name": "DarkSeeker", "bravery": 80}
)
# Output: "You conquered The Slasher's Den. Now The Occult Chamber beckons..."
```

---

## Testing

Run the comprehensive test suite:

```bash
cd c:\31000
python oracle_engine\test_lore_whisperer.py
```

This will demonstrate:
- Perfect performance lore
- Poor performance lore
- Wrathful Oracle scenario
- Cruel Oracle scenario
- Movie backstories
- Chamber transitions

---

## Future Enhancements

### LangChain Integration (Planned)
- Use LLM to generate truly unique lore fragments
- Load prompt template from `prompts/lore_whisperer_prompt.txt`
- Add context memory for continuity
- Generate lore based on specific movie themes

### Planned Features
- Theme-specific lore pools (slasher, occult, cosmic horror)
- Player relic references in lore
- Dynamic lore based on time of day
- Lore fragments that unlock "hidden knowledge"
- Oracle personality variations

---

## Architecture Notes

- **Standalone**: Node can operate independently of LangChain
- **Deterministic**: Repeatable results for testing
- **Fast**: <10ms generation time (rule-based)
- **Extensible**: Easy to add new lore templates
- **Context-aware**: Responds to emotion, theme, and performance

---

## File Locations

```
oracle_engine/
├── lore_whisperer_node.py         # Main node implementation
├── test_lore_whisperer.py         # Test suite
├── prompts/
│   └── lore_whisperer_prompt.txt  # Future LangChain prompt
└── LORE_WHISPERER_DOCUMENTATION.md  # This file
```

---

## Support

For questions or issues with the Lore Whisperer Node:
1. Run test suite to verify functionality
2. Check emotion mappings are valid
3. Ensure player_profile has required fields
4. Verify theme strings match expected values

---

*The Oracle whispers through the code... listen well.*

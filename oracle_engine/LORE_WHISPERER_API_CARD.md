# 🔮 Lore Whisperer - API Reference Card

```
╔══════════════════════════════════════════════════════════════════════╗
║                     LORE WHISPERER NODE - API                        ║
║              Generate Poetic Horror Fragments Between Chambers       ║
╚══════════════════════════════════════════════════════════════════════╝

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ IMPORT                                                             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

from oracle_engine.lore_whisperer_node import LoreWhispererNode

lore_node = LoreWhispererNode()


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ MAIN METHOD                                                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

lore = lore_node.whisper_between_chambers(
    player_profile = {
        "name": str,              # Player name
        "bravery": 0-100,         # Courage level
        "lore_knowledge": 0-100,  # Horror knowledge
        "fear_level": 0-100,      # Current fear
        "level": int              # Player level
    },
    last_theme = str,  # "slasher"|"occult"|"supernatural"|"psychological"...
    emotion = str,     # "pleased"|"amused"|"mocking"|"disappointed"|
                      #  "wrathful"|"cruel"|"indifferent"
    performance = str  # "excellent"|"good"|"average"|"poor" (optional)
)


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ OUTPUT STRUCTURE                                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{
  "lore_fragment": {
    "text":      str,    # 📜 The poetic horror text (5-15 words)
    "style":     str,    # Fragment style (see below)
    "intensity": float   # 0.0-1.0 darkness level
  },
  
  "atmosphere": {
    "mood":            str,      # Emotional atmosphere
    "visual_hints":    [str],    # 2-3 visual elements
    "ambient_sound":   str,      # Sound effect name
    "intensity_level": str       # "low"|"medium"|"high"
  },
  
  "oracle_voice": {
    "tone":            str,  # Oracle's tone
    "emotion":         str,  # Oracle's emotion
    "intimacy_level":  str,  # How close Oracle feels
    "volume":          str   # "whisper"|"normal"|"thunderous"
  },
  
  "narrative_hooks": {
    "references_last_theme": bool,  # References previous quiz?
    "foreshadows_next":      bool,  # Hints at next challenge?
    "personal_observation":  str,   # Personalized comment
    "hints_at_rewards":      bool   # Teases rewards?
  },
  
  "metadata": {
    "fragment_type":     str,  # Usually "transition"
    "trigger":           str,  # "quiz_completion"
    "duration_seconds":  int,  # 3-8 seconds
    "player_level":      int   # Player's level
  }
}


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ FRAGMENT STYLES                                                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

cryptic_prophecy      • Mysterious predictions and riddles
ancient_warning       • Ominous warnings from the past
mocking_observation   • Oracle taunts and ridicules
dark_wisdom           • Profound horror insights
eldritch_whisper      • Cosmic, incomprehensible horror


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ORACLE EMOTIONS → OUTPUT MAPPING                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Emotion         Mood          Style               Intensity  Volume
───────────────────────────────────────────────────────────────────
pleased         mysterious    dark_wisdom         0.3        normal
amused          eerie         mocking_observ.     0.5        normal
mocking         malevolent    mocking_observ.     0.7        normal
disappointed    ominous       cryptic_prophecy    0.6        normal
wrathful        suffocating   ancient_warning     0.9        thunderous
cruel           dread         ancient_warning     0.85       thunderous
indifferent     eerie         cryptic_prophecy    0.4        whisper


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ QUICK EXAMPLES                                                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

# Example 1: Perfect performance
lore = lore_node.whisper_between_chambers(
    {"name": "BloodSeeker", "bravery": 75, "lore_knowledge": 85,
     "fear_level": 30, "level": 3},
    "slasher", "pleased", "excellent"
)
# → "Knowledge gleams in the darkness, a rare light."


# Example 2: Poor performance
lore = lore_node.whisper_between_chambers(
    {"name": "Novice", "bravery": 40, "lore_knowledge": 35,
     "fear_level": 75, "level": 1},
    "occult", "mocking", "poor"
)
# → "Did you think occult would yield so easily?"


# Example 3: Wrathful Oracle
lore = lore_node.whisper_between_chambers(
    {"name": "FoolishMortal", "bravery": 30, "lore_knowledge": 25,
     "fear_level": 90, "level": 2},
    "supernatural", "wrathful", "poor"
)
# → "FOOL! The supernatural spirits howl at your ignorance!"


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ADDITIONAL METHODS                                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

# Generate movie backstory
backstory = lore_node.generate_backstory({
    "title": "The Exorcist",
    "year": 1973
})
# → "In 1973, The Exorcist emerged from the void—a curse captured 
#     on celluloid."


# Generate chamber transition
transition = lore_node.generate_transition(
    from_room="The Slasher's Den",
    to_room="The Occult Chamber",
    performance="excellent",
    player_profile=player
)
# → "You conquered The Slasher's Den. Now The Occult Chamber beckons..."


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ FRONTEND INTEGRATION                                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

# Display the lore text
display_text(lore["lore_fragment"]["text"])

# Apply atmosphere
set_mood(lore["atmosphere"]["mood"])
show_visuals(lore["atmosphere"]["visual_hints"])
play_sound(lore["atmosphere"]["ambient_sound"])

# Style Oracle's voice
style_voice(
    lore["oracle_voice"]["tone"],
    lore["oracle_voice"]["volume"],
    lore["oracle_voice"]["intimacy_level"]
)

# Show personal observation
if lore["narrative_hooks"]["personal_observation"]:
    show_message(lore["narrative_hooks"]["personal_observation"])

# Timing
duration = lore["metadata"]["duration_seconds"]
setTimeout(next_chamber, duration * 1000)


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ VISUAL & AUDIO ELEMENTS                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Visual Hints (random 2-3 per fragment):
  • flickering_candles     • shadow_figures      • blood_moon
  • cracked_mirrors        • writhing_shadows    • spectral_mist
  • ancient_runes          • decaying_walls      • crimson_light

Ambient Sounds (1 per fragment):
  • distant_whispers       • chains_rattling     • mournful_wind
  • dripping_water         • heartbeat_echo      • screaming_silence

Moods:
  • ominous    • dread       • eerie
  • malevolent • mysterious  • suffocating


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PERFORMANCE                                                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Generation Time:   < 10ms (deterministic, no AI)
Fragment Length:   5-15 words
Reading Duration:  3-8 seconds (auto-calculated)
Memory Usage:      Minimal (no caching)
Randomization:     Uses random.choice() for variety


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ FILES & DOCUMENTATION                                              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Implementation:    oracle_engine/lore_whisperer_node.py
Tests:             oracle_engine/test_lore_whisperer.py

Documentation:
  • LORE_WHISPERER_DOCUMENTATION.md      (Full API reference)
  • LORE_WHISPERER_QUICK_REFERENCE.md    (One-page cheat sheet)
  • LORE_WHISPERER_FLOW.md               (Architecture diagrams)
  • LORE_WHISPERER_API_CARD.md           (This file)
  • LORE_WHISPERER_SUMMARY.md            (Overview)


╔══════════════════════════════════════════════════════════════════════╗
║  "The Oracle whispers between the chambers..." 🔮                    ║
╚══════════════════════════════════════════════════════════════════════╝
```


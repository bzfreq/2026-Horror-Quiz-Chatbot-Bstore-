"""
Test script for the Lore Whisperer Node
Demonstrates generating poetic horror fragments between quiz chambers.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from oracle_engine.lore_whisperer_node import LoreWhispererNode


def print_lore_output(lore_data: dict, title: str = "LORE FRAGMENT"):
    """Pretty print lore output."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)
    
    # Lore Fragment
    fragment = lore_data.get("lore_fragment", {})
    print(f"\n[LORE TEXT]:")
    print(f'   "{fragment.get("text", "")}"')
    print(f"\n   Style: {fragment.get('style', 'N/A')}")
    print(f"   Intensity: {fragment.get('intensity', 0):.2f}")
    
    # Atmosphere
    atmosphere = lore_data.get("atmosphere", {})
    print(f"\n[ATMOSPHERE]:")
    print(f"   Mood: {atmosphere.get('mood', 'N/A')}")
    print(f"   Intensity: {atmosphere.get('intensity_level', 'N/A')}")
    print(f"   Visual Hints: {', '.join(atmosphere.get('visual_hints', []))}")
    print(f"   Ambient Sound: {atmosphere.get('ambient_sound', 'N/A')}")
    
    # Oracle Voice
    voice = lore_data.get("oracle_voice", {})
    print(f"\n[ORACLE VOICE]:")
    print(f"   Tone: {voice.get('tone', 'N/A')}")
    print(f"   Emotion: {voice.get('emotion', 'N/A')}")
    print(f"   Intimacy: {voice.get('intimacy_level', 'N/A')}")
    print(f"   Volume: {voice.get('volume', 'N/A')}")
    
    # Narrative Hooks
    hooks = lore_data.get("narrative_hooks", {})
    print(f"\n[NARRATIVE HOOKS]:")
    print(f"   References Last Theme: {hooks.get('references_last_theme', False)}")
    print(f"   Foreshadows Next: {hooks.get('foreshadows_next', False)}")
    print(f"   Personal Observation: \"{hooks.get('personal_observation', '')}\"")
    print(f"   Hints at Rewards: {hooks.get('hints_at_rewards', False)}")
    
    # Metadata
    metadata = lore_data.get("metadata", {})
    print(f"\n[METADATA]:")
    print(f"   Fragment Type: {metadata.get('fragment_type', 'N/A')}")
    print(f"   Trigger: {metadata.get('trigger', 'N/A')}")
    print(f"   Duration: {metadata.get('duration_seconds', 0)} seconds")
    print(f"   Player Level: {metadata.get('player_level', 0)}")


def test_scenario_1_perfect_performance():
    """Test: Player aces a slasher-themed quiz."""
    print("\n" + "#" * 70)
    print("  SCENARIO 1: Perfect Performance on Slasher Quiz")
    print("#" * 70)
    
    lore_node = LoreWhispererNode()
    
    player_profile = {
        "name": "BloodSeeker",
        "bravery": 75,
        "lore_knowledge": 85,
        "fear_level": 30,
        "level": 3,
        "relics": ["Jason's Mask", "Freddy's Glove"]
    }
    
    lore = lore_node.whisper_between_chambers(
        player_profile=player_profile,
        last_theme="slasher",
        emotion="pleased",
        performance="excellent"
    )
    
    print_lore_output(lore, "Oracle's Whisper After Victory")
    
    # Also show JSON output
    print(f"\n[RAW JSON OUTPUT]:")
    print(json.dumps(lore, indent=2))


def test_scenario_2_poor_performance():
    """Test: Player fails an occult-themed quiz."""
    print("\n" + "#" * 70)
    print("  SCENARIO 2: Poor Performance on Occult Quiz")
    print("#" * 70)
    
    lore_node = LoreWhispererNode()
    
    player_profile = {
        "name": "NoviceSeeker",
        "bravery": 40,
        "lore_knowledge": 35,
        "fear_level": 75,
        "level": 1
    }
    
    lore = lore_node.whisper_between_chambers(
        player_profile=player_profile,
        last_theme="occult",
        emotion="mocking",
        performance="poor"
    )
    
    print_lore_output(lore, "Oracle Mocks the Failing Student")


def test_scenario_3_wrathful_oracle():
    """Test: Oracle becomes wrathful after terrible performance."""
    print("\n" + "#" * 70)
    print("  SCENARIO 3: Wrathful Oracle After Repeated Failures")
    print("#" * 70)
    
    lore_node = LoreWhispererNode()
    
    player_profile = {
        "name": "FoolishMortal",
        "bravery": 30,
        "lore_knowledge": 25,
        "fear_level": 90,
        "level": 2
    }
    
    lore = lore_node.whisper_between_chambers(
        player_profile=player_profile,
        last_theme="supernatural",
        emotion="wrathful",
        performance="poor"
    )
    
    print_lore_output(lore, "The Oracle's FURY Unleashed")


def test_scenario_4_cruel_oracle():
    """Test: Oracle enjoys player's suffering."""
    print("\n" + "#" * 70)
    print("  SCENARIO 4: Cruel Oracle Savors Fear")
    print("#" * 70)
    
    lore_node = LoreWhispererNode()
    
    player_profile = {
        "name": "TremblingSeeker",
        "bravery": 35,
        "lore_knowledge": 60,
        "fear_level": 85,
        "level": 4
    }
    
    lore = lore_node.whisper_between_chambers(
        player_profile=player_profile,
        last_theme="psychological",
        emotion="cruel",
        performance="average"
    )
    
    print_lore_output(lore, "Oracle Feeds on Delicious Fear")


def test_movie_backstory():
    """Test movie backstory generation."""
    print("\n" + "#" * 70)
    print("  BONUS: Movie Backstory Generation")
    print("#" * 70)
    
    lore_node = LoreWhispererNode()
    
    movies = [
        {"title": "The Exorcist", "year": 1973},
        {"title": "Halloween", "year": 1978},
        {"title": "The Conjuring", "year": 2013}
    ]
    
    print("\n[HORROR FILM BACKSTORIES]:\n")
    for movie in movies:
        backstory = lore_node.generate_backstory(movie)
        print(f"   • {backstory}")


def test_transition_text():
    """Test transition text generation."""
    print("\n" + "#" * 70)
    print("  BONUS: Chamber Transition Texts")
    print("#" * 70)
    
    lore_node = LoreWhispererNode()
    
    player_profile = {
        "name": "DarkSeeker",
        "bravery": 60,
        "lore_knowledge": 70,
        "fear_level": 50,
        "level": 3
    }
    
    transitions = [
        ("The Slasher's Den", "The Occult Chamber", "excellent"),
        ("The Haunted Gallery", "The Blood Room", "average"),
        ("The Nightmare Pit", "The Final Trial", "poor")
    ]
    
    print("\n[CHAMBER TRANSITIONS]:\n")
    for from_room, to_room, perf in transitions:
        text = lore_node.generate_transition(from_room, to_room, perf, player_profile)
        print(f"   [{perf.upper()}] {text}\n")


def main():
    """Run all test scenarios."""
    print("\n")
    print("#" * 70)
    print("  LORE WHISPERER NODE - DEMONSTRATION")
    print("#" * 70)
    print("\n  Generating poetic horror fragments between quiz chambers...")
    
    # Run test scenarios
    test_scenario_1_perfect_performance()
    test_scenario_2_poor_performance()
    test_scenario_3_wrathful_oracle()
    test_scenario_4_cruel_oracle()
    test_movie_backstory()
    test_transition_text()
    
    print("\n" + "#" * 70)
    print("  DEMONSTRATION COMPLETE")
    print("#" * 70)
    print("\n  The Lore Whisperer awaits your call between the chambers...")
    print()


if __name__ == "__main__":
    main()


"""
Standalone test for Fear Meter Node
Tests the Oracle emotional state translation without requiring LangChain dependencies
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly from the module file to avoid __init__.py imports
import importlib.util
spec = importlib.util.spec_from_file_location("fear_meter_node", 
    os.path.join(os.path.dirname(__file__), "fear_meter_node.py"))
fear_meter_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fear_meter_module)
FearMeterNode = fear_meter_module.FearMeterNode


def test_fear_meter():
    """Test the Fear Meter with different accuracy scenarios."""
    print("=" * 70)
    print("HORROR ORACLE - FEAR METER TEST")
    print("=" * 70)
    
    # Sample player profile
    player = {
        "name": "DarkSeeker",
        "bravery": 65,
        "lore_knowledge": 70,
        "logic": 75,
        "fear_level": 50
    }
    
    # Test different accuracy scenarios
    scenarios = [
        (1.0, "Perfect Score", "Player gets everything right"),
        (0.85, "Excellent Performance", "Player demonstrates mastery"),
        (0.6, "Average Performance", "Player shows adequate knowledge"),
        (0.35, "Poor Performance", "Player struggles with answers"),
        (0.15, "Very Poor Performance", "Player fails most questions")
    ]
    
    fear_meter = FearMeterNode()
    previous_tone = "neutral"
    
    for accuracy, label, description in scenarios:
        print(f"\n{'='*70}")
        print(f"SCENARIO: {label}")
        print(f"Accuracy: {accuracy*100:.0f}% - {description}")
        print(f"{'='*70}")
        
        result = fear_meter.translate_to_oracle_state(
            accuracy=accuracy,
            previous_tone=previous_tone,
            player_profile=player
        )
        
        print(f"\n[ORACLE EMOTIONAL STATE]")
        print(f"   Tone: {result['oracle_tone'].upper()}")
        print(f"   Emotion: {result['oracle_emotion']}")
        print(f"   Intensity: {result['intensity']:.2f} / 1.0")
        print(f"   Next Tone: {result['next_tone']}")
        print(f"   Fear Shift: {result['fear_shift']:+.2f}")
        
        print(f"\n[PLAYER STATE]")
        print(f"   Confidence: {result['player_state']['confidence'].upper()}")
        print(f"   Fear Level: {result['player_state']['fear_level']} / 100")
        print(f"   Performance Trend: {result['player_state']['performance_trend']}")
        
        print(f"\n[ORACLE BEHAVIOR MODIFICATIONS]")
        print(f"   Difficulty Adjustment: {result['oracle_behavior']['difficulty_adjustment'].upper()}")
        print(f"   Reveal Lore: {'YES' if result['oracle_behavior']['reveal_lore'] else 'NO'}")
        print(f"   Mock Intensity: {result['oracle_behavior']['mock_intensity'].upper()}")
        rewards = result['oracle_behavior']['rewards_granted']
        print(f"   Rewards Granted: {', '.join(rewards) if rewards else 'None'}")
        
        print(f"\n[NARRATIVE ATMOSPHERE]")
        print(f"   Chamber Atmosphere: {result['narrative_context']['chamber_atmosphere']}")
        print(f"   Oracle Stance:")
        print(f"      {result['narrative_context']['oracle_stance']}")
        
        print(f"\n[ORACLE'S MESSAGE]")
        print(f'   "{result["atmospheric_message"]}"')
        
        print(f"\n[TRANSITION TO NEXT PHASE]")
        print(f"   {result['narrative_context']['transition_text']}")
        
        # Update for next iteration to show tone progression
        previous_tone = result['next_tone']
        player['fear_level'] = result['player_state']['fear_level']
        
        print(f"\n   > Player's fear level changed to: {player['fear_level']}")
    
    print(f"\n{'='*70}")
    print("TEST COMPLETE")
    print("The Fear Meter successfully translates quiz performance into")
    print("Oracle emotional states and behavioral modifications.")
    print(f"{'='*70}\n")


def test_tone_transitions():
    """Test tone transition logic."""
    print("\n" + "=" * 70)
    print("TESTING TONE TRANSITIONS")
    print("=" * 70)
    
    fear_meter = FearMeterNode()
    
    test_cases = [
        ("reverent", 0.95, "Previous: reverent, High accuracy"),
        ("mocking", 0.25, "Previous: mocking, Low accuracy"),
        ("neutral", 0.8, "Previous: neutral, Good accuracy"),
        ("disappointed", 0.5, "Previous: disappointed, Average accuracy"),
    ]
    
    player = {"name": "Tester", "bravery": 50, "lore_knowledge": 50, 
              "logic": 50, "fear_level": 50}
    
    for prev_tone, accuracy, desc in test_cases:
        result = fear_meter.translate_to_oracle_state(
            accuracy=accuracy,
            previous_tone=prev_tone,
            player_profile=player
        )
        
        print(f"\n{desc}")
        print(f"  Current Tone: {result['oracle_tone']}")
        print(f"  Next Tone: {result['next_tone']}")
        print(f"  Transition: {prev_tone} -> {result['oracle_tone']} -> {result['next_tone']}")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    test_fear_meter()
    test_tone_transitions()


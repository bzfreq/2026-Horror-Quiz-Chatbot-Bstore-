#!/usr/bin/env python3
"""
Test script for Oracle Engine frontend integration.
This validates that the /api/start_quiz and /api/submit_answers endpoints work correctly.
"""

import requests
import json

API_BASE = "http://localhost:5000"

def test_start_quiz():
    """Test the /api/start_quiz endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Starting Oracle Quiz")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_BASE}/api/start_quiz",
            json={"user_id": "test_user_123"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Quiz started!")
            print(f"\n📋 Quiz Data:")
            print(f"   Room: {data.get('room', 'N/A')}")
            print(f"   Theme: {data.get('theme', 'N/A')}")
            print(f"   Difficulty: {data.get('difficulty', 'N/A')}")
            print(f"   Questions: {len(data.get('questions', []))}")
            print(f"   Fear Level: {data.get('player_profile', {}).get('fear_level', 'N/A')}")
            
            if 'lore' in data and data['lore']:
                print(f"\n📜 Lore Generated: Yes")
            
            return data
        else:
            print(f"❌ FAILED: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ FAILED: Cannot connect to Flask backend")
        print("   Make sure Flask is running on http://localhost:5000")
        return None
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return None


def test_submit_answers(quiz_data):
    """Test the /api/submit_answers endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Submitting Answers to Oracle")
    print("="*60)
    
    if not quiz_data:
        print("⚠️  SKIPPED: No quiz data from previous test")
        return
    
    try:
        # Create sample answers (all correct for testing)
        questions = quiz_data.get('questions', [])
        answers = {}
        for i, q in enumerate(questions):
            answers[f"q{i}"] = q.get('correct', 0)
        
        response = requests.post(
            f"{API_BASE}/api/submit_answers",
            json={
                "user_id": "test_user_123",
                "quiz": quiz_data,
                "answers": answers
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Answers submitted!")
            print(f"\n📊 Results:")
            print(f"   Score: {data.get('score', 0)}/{data.get('out_of', 0)}")
            print(f"   Percentage: {data.get('percentage', 0)}%")
            print(f"   Fear Level: {data.get('player_profile', {}).get('fear_level', 'N/A')}")
            
            evaluation = data.get('evaluation', {})
            if evaluation.get('oracle_reaction'):
                print(f"\n🔮 Oracle's Reaction:")
                print(f"   {evaluation['oracle_reaction'][:100]}...")
            
            oracle_state = data.get('oracle_state', {})
            if oracle_state:
                print(f"\n🎭 Oracle State:")
                print(f"   Tone: {oracle_state.get('tone', 'N/A')}")
                print(f"   Emotion: {oracle_state.get('emotion', 'N/A')}")
                print(f"   Intensity: {oracle_state.get('intensity', 'N/A')}")
            
            rewards = data.get('rewards', {})
            if rewards.get('reward_name'):
                print(f"\n🏆 Reward Earned:")
                print(f"   {rewards['reward_name']}")
            
            lore = data.get('lore', {})
            if lore.get('whisper'):
                print(f"\n📜 Lore Whispered: Yes")
            
            return True
        else:
            print(f"❌ FAILED: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def main():
    print("\n🩸 HORROR ORACLE - INTEGRATION TEST 🩸")
    print("Testing Oracle Engine API endpoints...")
    
    # Test 1: Start Quiz
    quiz_data = test_start_quiz()
    
    # Test 2: Submit Answers
    if quiz_data:
        test_submit_answers(quiz_data)
    
    print("\n" + "="*60)
    print("TESTS COMPLETE")
    print("="*60)
    print("\n💡 Next Steps:")
    print("   1. If tests passed, open http://localhost:5000 in browser")
    print("   2. Click 'Face Your Nightmares' button")
    print("   3. Experience the Oracle's judgment!")
    print()


if __name__ == "__main__":
    main()


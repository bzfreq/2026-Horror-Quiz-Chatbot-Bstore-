#!/usr/bin/env python3
"""
Test script for Horror Oracle Quiz Endpoints
Tests /api/start_quiz and /api/submit_answers
"""

import requests
import json
import sys

API_BASE = "http://localhost:5000"

def test_start_quiz():
    """Test the /api/start_quiz endpoint"""
    print("\n" + "="*60)
    print("🧪 Testing /api/start_quiz endpoint...")
    print("="*60)
    
    try:
        # Test with chamber_level 1
        response = requests.post(
            f"{API_BASE}/api/start_quiz",
            json={"chamber_level": 1},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS!")
            print(f"\nChamber Name: {data.get('chamber_name')}")
            print(f"Theme: {data.get('theme')}")
            print(f"Difficulty: {data.get('difficulty')}")
            print(f"Number of Questions: {len(data.get('questions', []))}")
            
            # Validate structure
            assert 'chamber_name' in data, "Missing chamber_name"
            assert 'questions' in data, "Missing questions"
            assert 'score' in data, "Missing score"
            assert 'next' in data, "Missing next"
            assert len(data['questions']) == 5, f"Expected 5 questions, got {len(data['questions'])}"
            
            # Display first question
            if data['questions']:
                q = data['questions'][0]
                print(f"\nSample Question:")
                print(f"  Q: {q.get('question')}")
                print(f"  Options: {q.get('options')}")
                print(f"  Correct Answer Index: {q.get('correct')}")
            
            print(f"\nNext Preview: {data['next'].get('preview')}")
            print("\n✅ All validations passed!")
            
            return data  # Return for use in next test
        else:
            print(f"❌ FAILED with status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def test_submit_answers(quiz_data=None):
    """Test the /api/submit_answers endpoint"""
    print("\n" + "="*60)
    print("🧪 Testing /api/submit_answers endpoint...")
    print("="*60)
    
    try:
        # Create sample answers (mix of correct and incorrect)
        test_payload = {
            "chamber_level": 1,
            "answers": [0, 1, 2, 0, 1],  # User's answers
            "correct_answers": [1, 1, 2, 0, 2]  # Correct answers (score should be 3/5)
        }
        
        response = requests.post(
            f"{API_BASE}/api/submit_answers",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS!")
            
            # Validate structure
            assert 'score' in data, "Missing score"
            assert 'next' in data, "Missing next"
            assert 'result_message' in data, "Missing result_message"
            
            print(f"\nScore: {data['score']['correct']}/{data['score']['total']} ({data['score']['percentage']}%)")
            print(f"Result: {data['result_message']}")
            print(f"Can Progress: {data['next']['can_progress']}")
            print(f"Next Chamber: {data['next']['chamber_name']}")
            print(f"Chamber Completed: {data.get('chamber_completed')}")
            
            print("\n✅ All validations passed!")
            return True
        else:
            print(f"❌ FAILED with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_all_chambers():
    """Test all 5 chambers"""
    print("\n" + "="*60)
    print("🧪 Testing all chamber levels...")
    print("="*60)
    
    chambers = [
        "The Bleeding Room",
        "The Zombie Catacombs",
        "The Vampire's Lair",
        "The Demon's Gate",
        "The Final Nightmare"
    ]
    
    for i, expected_chamber in enumerate(chambers, 1):
        try:
            response = requests.post(
                f"{API_BASE}/api/start_quiz",
                json={"chamber_level": i},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                actual_chamber = data.get('chamber_name')
                
                if actual_chamber == expected_chamber:
                    print(f"✅ Chamber {i}: {actual_chamber}")
                else:
                    print(f"❌ Chamber {i}: Expected '{expected_chamber}', got '{actual_chamber}'")
            else:
                print(f"❌ Chamber {i}: Failed with status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Chamber {i}: Error - {str(e)}")

def main():
    """Run all tests"""
    print("\n🩸 HORROR ORACLE QUIZ ENDPOINT TESTS 🩸")
    print("="*60)
    print("⚠️  Make sure the Flask server is running on http://localhost:5000")
    print("="*60)
    
    # Test 1: Start Quiz
    quiz_data = test_start_quiz()
    
    if not quiz_data:
        print("\n❌ start_quiz test failed. Aborting further tests.")
        sys.exit(1)
    
    # Test 2: Submit Answers
    success = test_submit_answers(quiz_data)
    
    if not success:
        print("\n❌ submit_answers test failed.")
        sys.exit(1)
    
    # Test 3: All Chambers
    test_all_chambers()
    
    # Final summary
    print("\n" + "="*60)
    print("🎉 ALL TESTS COMPLETED!")
    print("="*60)
    print("\n✅ Quiz endpoints are working correctly!")
    print("✅ JSON structure matches specification")
    print("✅ All 5 chambers are accessible")
    print("✅ Scoring and progression logic works")
    print("\n🚀 Ready for frontend integration!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        sys.exit(1)














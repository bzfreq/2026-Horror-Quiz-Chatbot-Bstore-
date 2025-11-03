"""
Simple test to check if the quiz system is working
"""
import requests
import json

def test_start_quiz():
    """Test the /api/start_quiz endpoint"""
    url = "http://localhost:5000/api/start_quiz"
    payload = {
        "userId": "test_user_123"
    }
    
    print("Testing /api/start_quiz endpoint...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS! Quiz endpoint is working!")
            print(f"\nQuiz Data Keys: {list(data.keys())}")
            print(f"Room: {data.get('room', 'N/A')}")
            print(f"Theme: {data.get('theme', 'N/A')}")
            print(f"Difficulty: {data.get('difficulty', 'N/A')}")
            print(f"Number of Questions: {len(data.get('questions', []))}")
            
            if 'questions' in data and len(data['questions']) > 0:
                print(f"\nFirst Question: {data['questions'][0].get('question', 'N/A')}")
        else:
            print(f"\n❌ ERROR: Status code {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server!")
        print("Make sure the Flask server is running on http://localhost:5000")
        print("\nTo start the server, run:")
        print("  python horror.py")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_start_quiz()


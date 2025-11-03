"""Quick test to check if the Horror Oracle backend is responding correctly"""
import requests
import time

API_BASE = "http://localhost:5000"

print("Testing Horror Oracle Backend...")
print("=" * 60)

# Test 1: Check if backend is running
try:
    print("\n1. Testing if backend is accessible...")
    response = requests.get(f"{API_BASE}/", timeout=5)
    print(f"   [OK] Backend is running (status: {response.status_code})")
except Exception as e:
    print(f"   [ERROR] Backend is NOT running: {e}")
    print("\n   Please start the backend first:")
    print("   - Run: python app.py")
    print("   - Or double-click: START_HERE_FIRST.bat")
    print("   - Or double-click: RUN_BACKEND.bat")
    exit(1)

# Test 2: Check Oracle Engine quiz generation
try:
    print("\n2. Testing Oracle Engine quiz generation...")
    print("   (This may take 10-30 seconds if using OpenAI...)")
    
    start_time = time.time()
    response = requests.post(
        f"{API_BASE}/api/start_quiz",
        json={"user_id": "test_user"},
        timeout=60  # 60 second timeout
    )
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        print(f"   [OK] Quiz generated successfully in {elapsed:.1f} seconds")
        print(f"   - Questions: {len(data.get('questions', []))}")
        print(f"   - Theme: {data.get('theme', 'N/A')}")
        print(f"   - Difficulty: {data.get('difficulty', 'N/A')}")
        print(f"   - Room: {data.get('room', 'N/A')}")
        
        if data.get('questions') and len(data.get('questions')) > 0:
            print(f"\n   Sample question:")
            first_q = data['questions'][0]
            print(f"   Q: {first_q.get('question', 'N/A')[:80]}...")
            print(f"   Choices: {len(first_q.get('choices', []))} options")
    else:
        print(f"   [ERROR] HTTP {response.status_code}")
        print(f"   Response: {response.text}")
        
except requests.exceptions.Timeout:
    print(f"   [ERROR] Request timed out after 60 seconds")
    print("\n   This could mean:")
    print("   - OpenAI API is slow or not responding")
    print("   - Network connectivity issues")
    print("   - Check OpenAI API status: https://status.openai.com")
    print("\n   Suggestions:")
    print("   - Check your internet connection")
    print("   - Verify OPENAI_API_KEY in .env file")
    print("   - Try again in a few moments")
except Exception as e:
    print(f"   [ERROR] {e}")

print("\n" + "=" * 60)
print("Test complete!")
print("\nIf backend is working, you can now:")
print("1. Open browser to http://localhost:5000")
print("2. Click Blood Quiz button")
print("3. Wait 10-30 seconds for quiz to generate")


# How to Start the Horror Oracle Backend

## The Problem
Your quiz is getting stuck because the **backend server is not running**.

The frontend is trying to connect to `http://localhost:5000` but there's no server listening.

## Solution - Start the Backend Server

### Option 1: Use the Batch File (EASIEST)
1. Double-click `RUN_BACKEND.bat` in your project folder
2. A command window will open
3. Wait for the message: "Running on http://127.0.0.1:5000"
4. Keep this window open while using the app

### Option 2: Manual Start
1. Open Command Prompt or PowerShell
2. Navigate to your project folder:
   ```
   cd C:\31000
   ```
3. Run the backend:
   ```
   python app.py
   ```
4. Wait for: "Running on http://127.0.0.1:5000"
5. Keep this window open

## Verify It's Working

### Method 1: Quick Test
1. Open a NEW command prompt (keep the backend running in the other one)
2. Run:
   ```
   cd C:\31000
   python test_backend_quick.py
   ```
3. You should see:
   ```
   [OK] Backend is running
   [OK] Quiz generated successfully
   ```

### Method 2: Browser Test
1. Open your browser
2. Go to: http://localhost:5000
3. You should see your Horror Oracle website

## What to Expect

When the backend starts correctly, you'll see:
```
==================================================
   HORROR ORACLE - FLASK + LANGCHAIN BACKEND
==================================================

Server running on http://localhost:5000
OpenAI: CONNECTED
Pinecone: CONNECTED (or DISCONNECTED - that's OK)
TMDB API: CONNECTED
OMDB API: CONNECTED (or MISSING - that's OK)
==================================================
```

## Common Issues

### Port Already in Use
If you see "Address already in use":
1. Another program is using port 5000
2. Stop any other Python/Flask servers
3. Or change the port in `app.py`

### Missing Dependencies
If you see import errors:
```
pip install -r requirements.txt
```

### No OpenAI Key
If OpenAI is "MISSING":
1. Check your `.env` file exists
2. Make sure it contains: `OPENAI_API_KEY=your_key_here`
3. Restart the backend

## Testing the Quiz

Once the backend is running:
1. Open http://localhost:5000 in your browser
2. Click the Blood Quiz button
3. The quiz should load within 10-30 seconds
4. Check the browser console (F12) for detailed loading logs

## Important Notes

- **Keep the backend window open** - closing it stops the server
- The first quiz generation takes 10-30 seconds (OpenAI API call)
- Subsequent quizzes are also fresh but may be faster
- If it takes longer than 30 seconds, check your internet connection

## Still Having Issues?

1. Check the backend console for error messages
2. Check the browser console (F12) for frontend errors
3. Make sure your `.env` file has valid API keys
4. Try restarting both backend and browser


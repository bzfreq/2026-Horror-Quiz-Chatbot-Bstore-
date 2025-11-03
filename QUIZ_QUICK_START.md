# 🩸 Horror Oracle Quiz - Quick Start Guide

## Start Using the Quiz System in 3 Steps

---

## Step 1: Start the Flask Backend

Open a terminal and run:

```bash
cd c:\31000
python horror.py
```

You should see:
```
==================================================
🩸 HORROR ORACLE AWAKENING... 🩸
==================================================
📊 Server running on http://localhost:5000
🎬 OMDB API: CONNECTED
🎥 TMDB API: CONNECTED
🧠 OpenAI: CONNECTED (or MISSING - Using fallback responses)
📦 Pinecone: CONNECTED
==================================================
```

**✅ Server is running successfully!**

---

## Step 2: Test the Endpoints (Optional)

Open a **new terminal** and run:

```bash
cd c:\31000
python test_quiz_endpoints.py
```

This will verify both endpoints are working correctly.

Expected output:
```
🧪 Testing /api/start_quiz endpoint...
✅ SUCCESS!

Chamber Name: The Bleeding Room
Theme: slashers
Difficulty: beginner
Number of Questions: 5

🧪 Testing /api/submit_answers endpoint...
✅ SUCCESS!

Score: 3/5 (60.0%)
Result: 👹 You escaped... barely.
```

---

## Step 3: Open the Frontend

1. Open `index.html` in your browser:
   ```
   file:///c:/31000/index.html
   ```
   
   OR use the live server if already running.

2. The quiz system is now fully functional!
   - Click any movie's **"🩸 Blood Quiz"** button
   - The quiz will load with 5 questions
   - Answer questions to progress through horror chambers

---

## 🎮 Using the Quiz System

### From the Main Interface:

1. **Search for a Horror Movie:**
   - Type any horror movie name in the chat
   - Example: "Halloween", "The Exorcist", "Saw"

2. **Click the Blood Quiz Button:**
   - After a movie loads, you'll see: **🩸 Blood Quiz**
   - Click it to start the quiz

3. **Answer 5 Questions:**
   - Each quiz has 5 themed questions
   - Based on horror chambers (Slashers, Zombies, Vampires, etc.)

4. **Get Your Score:**
   - Need 2+ correct to progress to next chamber
   - Perfect score (5/5): "🩸 PERFECT! You've survived!"
   - Good score (3-4): "👹 You escaped... barely."
   - Okay score (2): "🔪 You're bleeding out but alive."
   - Failed (0-1): "💀 The chamber has claimed you."

5. **Progress Through Chambers:**
   - Chamber 1: **The Bleeding Room** (Slashers)
   - Chamber 2: **The Zombie Catacombs** (Zombies)
   - Chamber 3: **The Vampire's Lair** (Vampires)
   - Chamber 4: **The Demon's Gate** (Demons)
   - Chamber 5: **The Final Nightmare** (Cult Horror)

---

## 🔧 Troubleshooting

### Quiz Button Doesn't Work?

**Check 1: Is the backend running?**
```bash
# Should see Flask server output
python horror.py
```

**Check 2: Correct port?**
- Backend runs on port **5000** by default
- Check `script-js-combined.js` line 13: `const API_BASE = 'http://localhost:5000';`

**Check 3: Check browser console**
- Open Developer Tools (F12)
- Look for errors in Console tab
- Common issue: CORS errors (server not running)

### Questions Don't Load?

**Option 1: OpenAI Key Available**
- Quiz will generate dynamic questions
- More variety and themed content

**Option 2: No OpenAI Key**
- Quiz uses 125 curated fallback questions
- Still fully functional!
- Questions are stored in `horror.py` lines 1339-1374

### Port Already in Use?

If port 5000 is already taken:

**Update Backend:**
Edit `horror.py` line 1793:
```python
app.run(host="0.0.0.0", port=8000, debug=True)
```

**Update Frontend:**
Edit `script-js-combined.js` line 13:
```javascript
const API_BASE = 'http://localhost:8000';
```

---

## 📊 Features Included

✅ **Dynamic Question Generation**
- Uses OpenAI to create varied questions
- Falls back to curated questions if needed

✅ **5 Themed Horror Chambers**
- Each with unique theme and difficulty
- Progressive challenge system

✅ **Score Tracking**
- Calculates correct/total
- Determines progression
- Shows percentage

✅ **User Progress Persistence**
- Saves quiz completion (if logged in)
- Tracks chamber progress
- Shows next chamber preview

✅ **Horror-Themed Feedback**
- Immersive messages based on score
- Chamber-specific atmosphere
- Engaging user experience

---

## 🔍 API Endpoints Reference

### Start a New Quiz
```
POST http://localhost:5000/api/start_quiz
Content-Type: application/json

{
  "chamber_level": 1
}
```

### Submit Quiz Answers
```
POST http://localhost:5000/api/submit_answers
Content-Type: application/json

{
  "chamber_level": 1,
  "answers": [1, 0, 2, 1, 3],
  "correct_answers": [1, 2, 2, 1, 0]
}
```

---

## 📚 Documentation Files

- **QUIZ_IMPLEMENTATION_SUMMARY.md** - Complete overview of changes
- **QUIZ_ENDPOINTS_DOCUMENTATION.md** - Technical API documentation
- **test_quiz_endpoints.py** - Automated test script
- **QUIZ_QUICK_START.md** - This file

---

## ✅ System Status

| Component | Status | Notes |
|-----------|--------|-------|
| Backend Routes | ✅ Working | `/api/start_quiz` and `/api/submit_answers` |
| Question Generation | ✅ Working | OpenAI + Fallback |
| Score Calculation | ✅ Working | Evaluates answers correctly |
| User Persistence | ✅ Working | Saves to user_data.json |
| Frontend Integration | ✅ Ready | No changes needed |
| Error Handling | ✅ Complete | Comprehensive error responses |

---

## 🎉 You're Ready!

The Horror Oracle quiz system is fully functional and ready to use.

**Next Actions:**
1. Start the backend: `python horror.py`
2. Open the frontend: `index.html`
3. Click any movie's **Blood Quiz** button
4. Enjoy the horror chambers!

**Need Help?**
- Check the console output for errors
- Run `python test_quiz_endpoints.py` to verify endpoints
- Review `QUIZ_ENDPOINTS_DOCUMENTATION.md` for API details

---

*Happy Horror Quizzing! 🩸*







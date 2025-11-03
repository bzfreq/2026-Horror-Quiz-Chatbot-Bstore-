# Quick Test Guide - Quiz Flow

## 🚀 Quick Start Test

### Step 1: Start Backend
```bash
python horror.py
```

### Step 2: Open Browser
```
http://localhost:5000
```

### Step 3: Test Flow

#### Test A: First → Second Quiz Transition
1. Click **"Face Your Nightmares"** button (green glowing button in header)
2. Wait for quiz to load
3. Answer all 5 questions (any answers)
4. Click **"Submit"** after answering all questions
5. Review Oracle's judgment
6. Click **"🔮 NEXT TRIAL"** button
7. **Expected Result:**
   - ✅ New chamber name appears (different from first)
   - ✅ New questions load
   - ✅ Console shows: `"✅ Next quiz loaded"`
   - ✅ Console shows: `"🎃 New Chamber: [name]"`

#### Test B: Modal Layout
1. Start a quiz
2. **Check:**
   - ✅ Modal is centered on screen
   - ✅ Modal is wide enough (800px or 80% of screen)
   - ✅ Text is readable
   - ✅ Content fits nicely

#### Test C: Horror Questions
1. Start multiple quizzes
2. **Check:**
   - ✅ Questions have cinematic atmosphere
   - ✅ Questions use horror vocabulary
   - ✅ Questions vary in theme

---

## 🐛 Debug Console Logs

Open browser console (F12) and look for:

```
✅ Oracle Quiz Data: {...}
✅ Questions Generated: 5
📝 First Question: In the silence of the abandoned asylum...
🎃 New Chamber: The Crypt of Eternal Damnation
📋 Quiz Theme: psychological
⚡ Difficulty: intermediate
🔮 Tone: creepy
```

---

## ✅ Success Criteria

### First Quiz Loads:
- ✅ 5 questions appear
- ✅ Questions have horror atmosphere
- ✅ Chamber name displayed

### Submit Answers:
- ✅ Oracle reaction appears
- ✅ Score displayed
- ✅ Fear level updated
- ✅ "NEXT TRIAL" button visible

### Second Quiz Loads:
- ✅ Old questions cleared
- ✅ New chamber name (different)
- ✅ New questions appear
- ✅ Console logs confirm

---

## 🔍 What to Look For

### Good Signs:
- Chamber names change between quizzes
- Questions have atmospheric intros
- Modal is centered and readable
- Transitions are smooth

### Bad Signs (Should NOT Happen):
- ❌ Second quiz shows same questions as first
- ❌ Modal is off-center or too narrow
- ❌ Old questions still visible
- ❌ Console errors about undefined quiz data

---

## 📊 Expected Console Output Sequence

```
1. User clicks "Face Your Nightmares"
   🔮 Starting Oracle Quiz...
   🔄 Calling /api/start_quiz - generating NEW questions...

2. Quiz loads
   ✅ Oracle Quiz Data: {...}
   ✅ Questions Generated: 5
   🎃 New Chamber: The Chamber of Whispers and Blood

3. User answers questions and submits
   🔮 Submitting answers to Oracle...
   ✅ Oracle Evaluation Result: {...}

4. User clicks "NEXT TRIAL"
   🔮 Starting Oracle Quiz...
   🔄 Calling /api/start_quiz - generating NEW questions...

5. Second quiz loads
   🧹 Cleared old quiz HTML
   ✅ Next quiz loaded
   🎃 New Chamber: The Abyss of Eternal Damnation
```

---

## 🎬 Video Walkthrough (Steps)

1. **Start app** → Homepage loads
2. **Click green button** → Quiz modal opens
3. **See chamber intro** → "The Chamber of..."
4. **Click "BEGIN THE TRIAL"** → First question appears
5. **Answer 5 questions** → Progress bar fills
6. **Click submit** → Oracle judges you
7. **Click "NEXT TRIAL"** → Old content clears
8. **New chamber appears** → Different name
9. **New questions load** → Different content
10. **Success!** → Flow works perfectly

---

## 🚨 Troubleshooting

### Issue: Second quiz doesn't load
**Solution:** Check console for errors. Look for:
- `"❌ Error starting Oracle quiz"`
- `"🔄 Retrying Oracle connection in 3 seconds..."`

If retry happens, wait 3 seconds for automatic retry.

### Issue: Modal is too small
**Solution:** Check CSS in browser dev tools:
- `.quiz-content` should have `max-width: 800px`
- Should have `width: 80%`

### Issue: Questions aren't atmospheric
**Solution:** 
- If using LLM: Check OpenAI API key is set
- If using fallback: Questions should still have atmosphere

---

## ✅ All Tests Pass When:

1. ✅ First quiz loads with chamber name
2. ✅ Questions have horror atmosphere
3. ✅ Submit works and shows Oracle reaction
4. ✅ "NEXT TRIAL" button appears
5. ✅ Click "NEXT TRIAL" → second quiz loads
6. ✅ Second quiz has DIFFERENT chamber name
7. ✅ Second quiz has NEW questions
8. ✅ Modal is centered and readable
9. ✅ Console logs are clean (no errors)
10. ✅ Transitions are smooth

---

## 🎉 Done!

If all tests pass, the second quiz transition fix is working perfectly! 🎃


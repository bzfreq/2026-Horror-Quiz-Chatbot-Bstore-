# Testing Quiz Uniqueness - Quick Guide

## 🧪 Quick Test Instructions

### Prerequisites
1. Make sure backend is running:
   ```bash
   python horror.py
   # Wait for: "Running on http://localhost:5000"
   ```

2. Open browser to your Horror Oracle app
3. Open Browser Console (F12 or Ctrl+Shift+I)

---

## Test Scenario 1: Verify Unique Chambers

### Step 1: Start First Quiz
1. Click "Start Quiz" or "Blood Quiz" button
2. **Check Console Output:**
   ```
   🎃 New Chamber: <chamber_name_1>
   📋 Quiz Theme: <theme_1>
   ⚡ Difficulty: <difficulty_1>
   ```
3. **Write down:** Chamber name, theme, difficulty

### Step 2: Complete First Quiz
1. Answer all 5 questions (any answers are fine)
2. Click "Submit" or "Complete Quiz"
3. **Check Console Output:**
   ```
   ✅ Score: X/5
   🎯 Next Difficulty: <difficulty_2>
   🎨 Next Theme: <theme_2>
   ```
4. **Verify:** Next theme is DIFFERENT from theme_1

### Step 3: Start Second Quiz
1. Click "NEXT TRIAL" button
2. **Check Console Output:**
   ```
   🔄 Using recommended difficulty: <difficulty_2>
   🔄 Using recommended theme: <theme_2>
   🎃 New Chamber: <chamber_name_2>
   ```
3. **Verify:**
   - ✅ chamber_name_2 ≠ chamber_name_1
   - ✅ theme_2 ≠ theme_1
   - ✅ Questions are different (compare first question)

### Step 4: Repeat
1. Complete second quiz
2. Start third quiz
3. **Verify again:** All chambers, themes, questions are unique

---

## Test Scenario 2: Verify Difficulty Adaptation

### High Performance Test
1. **Quiz 1:** Start at "intermediate" difficulty
2. **Answer:** Get 5/5 correct (100%)
3. **Submit → Check Console:**
   ```
   🎯 Next Difficulty: advanced  (should increase)
   ```
4. **Next Quiz:** Difficulty should be "advanced"

### Low Performance Test
1. **Quiz 1:** Start at "intermediate" difficulty
2. **Answer:** Get 1/5 correct (20%)
3. **Submit → Check Console:**
   ```
   🎯 Next Difficulty: beginner  (should decrease)
   ```
4. **Next Quiz:** Difficulty should be "beginner"

---

## Test Scenario 3: Verify Question Uniqueness

### Open Backend Terminal
While testing, watch backend terminal for:
```
[BUILDER NODE] Session UUID: abc12345 | Seed: 789012
[BUILDER NODE] Generating NEW questions (no cache)
```

Each quiz should show:
- ✅ Different Session UUID
- ✅ Different Seed number
- ✅ "Generating NEW questions" message

---

## Expected Console Output Example

### First Quiz Start:
```
🔮 Starting Oracle Quiz...
🔄 Calling /api/start_quiz - generating NEW questions...
📞 Fetching fresh quiz from Oracle Engine Builder Node...
✅ Oracle Engine response: {room: "The Crypt of Shadows and Blood", ...}
🎃 New Chamber Loaded: The Crypt of Shadows and Blood
📋 Theme: general_horror | ⚡ Difficulty: intermediate
[DEBUG] Questions received: 5
[DEBUG] First question: In what forgotten asylum did...
🎃 New Chamber: The Crypt of Shadows and Blood
📋 Quiz Theme: general_horror
⚡ Difficulty: intermediate
🔮 Tone: creepy
```

### After Submission:
```
✅ Oracle Evaluation Result: {score: 4, out_of: 5, ...}
🎯 Next Difficulty: advanced
🎨 Next Theme: psychological
```

### Second Quiz Start:
```
🔮 Starting Oracle Quiz...
🎯 Using recommended difficulty: advanced
🎨 Using recommended theme: psychological
📞 Fetching fresh quiz from Oracle Engine Builder Node...
🎃 New Chamber Loaded: The Abyss of Madness & Delusion
📋 Theme: psychological | ⚡ Difficulty: advanced
[DEBUG] First question: What psychiatric phenomenon drives...
🎃 New Chamber: The Abyss of Madness & Delusion
📋 Quiz Theme: psychological
⚡ Difficulty: advanced
```

---

## ✅ Success Checklist

After 3-5 quiz cycles, verify:

- [ ] Every chamber name is unique
- [ ] Every theme changes between quizzes
- [ ] Questions are never repeated
- [ ] Difficulty adapts based on performance
- [ ] Console shows unique UUID and seed each time
- [ ] Backend logs show different session IDs

---

## 🐛 Troubleshooting

### Issue: Same chamber name appears twice
**Possible Cause:** Random collision (unlikely but possible)
**Solution:** Run 5+ quizzes - should not repeat again

### Issue: Same questions appear
**Check:**
1. Backend terminal shows new UUID/seed?
2. LLM is being called (not using fallback)?
3. Is OpenAI API key valid?

**Debug:**
```javascript
// In browser console
console.log(oracleState);
// Should show nextDifficulty and nextTheme
```

### Issue: Theme doesn't change
**Check:**
```javascript
// In browser console after submitting quiz
console.log(oracleState.nextTheme);
// Should show a different theme than current
```

**Fix:** Make sure you're clicking "NEXT TRIAL" button (not starting fresh)

---

## 🎯 What to Report

If you find duplicates, report:
1. Chamber names that repeated
2. Question text that repeated
3. Console log output
4. Backend terminal output
5. Number of quizzes completed before duplicate

---

## Expected Results Summary

**After 10 Quizzes:**
- 10 unique chamber names ✅
- 10 different theme combinations ✅
- 50 unique questions (5 per quiz) ✅
- Difficulty adapted 2-3 times ✅
- No exact duplicates in any category ✅

---

## 🎉 If All Tests Pass

**You have successfully verified:**
- ✅ Unique quiz generation system is working
- ✅ Adaptive difficulty is functioning
- ✅ Theme rotation is active
- ✅ No duplicate questions across sessions
- ✅ Chamber names are always unique

**The Horror Oracle is now generating truly unique, adaptive quizzes!** 🎃


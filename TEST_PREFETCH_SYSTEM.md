# Test Guide: Simplified Prefetch System

## Quick Test Instructions

### 1. Start the Backend
```bash
python horror.py
```

### 2. Open the App
Navigate to `http://localhost:5000`

### 3. Test the Prefetch Flow

#### Test 1: Initial Quiz Start
1. Click "Face Your Nightmares" or start any quiz
2. **Watch console logs** - you should see:
   ```
   ✅ Starting quiz with X questions
   🔄 Prefetching next quiz in background...
   ```
3. Answer the quiz questions
4. **Check console** - you should see:
   ```
   ✅ Prefetched next quiz
   ```

#### Test 2: Submit & Continue (Fast Path)
1. Complete the quiz and submit answers
2. **Watch console** - should show:
   ```
   🔮 Submitting answers to Oracle...
   ✅ Oracle Evaluation Result
   🔄 Prefetching next quiz in background...
   ```
3. Click "▶️ CONTINUE TRIAL" button
4. **Should load INSTANTLY** with console showing:
   ```
   🚀 Using cached quiz - INSTANT
   ```

#### Test 3: Slow Path (No Cache)
1. Start a quiz
2. **Before prefetch completes**, try to continue
3. Should show:
   ```
   ⚠️ Cache empty, fetching live (slow path)
   ```
4. Quiz should still load, just slower

---

## Console Log Patterns

### ✅ Perfect Flow (Everything Working)
```
[User starts quiz]
✅ Starting quiz with 5 questions
🔄 Prefetching next quiz in background...

[User plays quiz - prefetch completes in background]
✅ Prefetched next quiz

[User submits]
🔮 Submitting answers to Oracle...
✅ Oracle Evaluation Result
🔄 Prefetching next quiz in background...

[User clicks continue]
🚀 Using cached quiz - INSTANT
✅ Next quiz loaded!
🔄 Prefetching next quiz in background...
```

### ⚠️ Slow Network (Fallback Working)
```
[User clicks continue before prefetch completes]
⚠️ Cache empty, fetching live (slow path)
[...fetching...]
✅ Next quiz loaded!
```

### ❌ Error Conditions
```
Prefetch failed: [error details]
```
This is OK - quiz will still work, just won't be instant.

---

## Performance Benchmarks

### Expected Timing:
- **First quiz load:** 2-4 seconds (normal, includes LLM generation)
- **Continue with cache:** < 300ms (instant! ⚡)
- **Continue without cache:** 2-4 seconds (same as first load)

### Check Network Tab:
1. Open DevTools → Network tab
2. Start quiz → should see 1 POST to `/api/start_quiz`
3. Watch for background prefetch → another POST to `/api/start_quiz`
4. Click continue → **no network request if cache hit!** ⚡

---

## Troubleshooting

### Problem: Prefetch not starting
**Check:**
- Is `prefetchNextQuiz()` being called?
- Check console for errors
- Verify `oracleState.userId` is set

### Problem: Cache not being used
**Check:**
- Does console show "Using cached quiz"?
- Check if `nextQuizCache` is null (cache expired/cleared)
- Verify prefetch completed before continue was clicked

### Problem: Duplicate prefetch calls
**Check:**
- Should see only ONE prefetch per cycle
- `prefetchInProgress` flag should prevent duplicates
- If seeing multiple, check for extra trigger points

---

## API Endpoint Verification

### Test `/api/start_quiz` Directly:

```bash
curl -X POST http://localhost:5000/api/start_quiz \
  -H "Content-Type: application/json" \
  -d '{"userId":"test","difficulty":"intermediate","theme":"general_horror"}'
```

**Expected Response:**
```json
{
  "questions": [...],
  "theme": "general_horror",
  "difficulty": "intermediate",
  "room": "Chamber Name",
  "intro": "...",
  "lore": {...}
}
```

---

## Success Criteria

✅ **Must Work:**
1. First quiz loads normally
2. Prefetch starts in background
3. Continue button loads instantly when cache ready
4. Falls back gracefully if cache empty
5. No duplicate prefetch calls
6. No console errors

⚡ **Performance:**
1. Continue should be < 500ms with cache
2. No blocking UI during prefetch
3. Smooth transitions between quizzes

🔧 **Code Quality:**
1. Clean console logs
2. No linter errors
3. Handles errors gracefully

---

## Automated Test Script (Browser Console)

Paste this in browser console to test the flow:

```javascript
// Test prefetch system
console.log('🧪 Testing Prefetch System...');

// Check global state
console.log('nextQuizCache:', nextQuizCache);
console.log('prefetchInProgress:', prefetchInProgress);

// Simulate prefetch
console.log('Starting prefetch test...');
prefetchNextQuiz().then(() => {
    console.log('✅ Prefetch test complete');
    console.log('Cache populated:', nextQuizCache !== null);
});
```

---

**Ready to test!** 🎮



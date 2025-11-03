# 🎭 Horror Oracle - Quick Reference Card

## 🚀 One-Minute Start

```bash
python horror.py
# Open: http://localhost:5000
# Click: "Face Your Nightmares"
```

---

## 📂 Key Files

| File | What Changed |
|------|-------------|
| `script-js-combined.js` | Added Oracle integration functions |
| `index.html` | Added fear level CSS + changed button |
| `horror.py` | Already had `/api/start_quiz` and `/api/submit_answers` |

---

## 🔧 New JavaScript Functions

```javascript
// Start Oracle quiz
startOracleQuiz()

// Display quiz with intro
displayOracleQuiz(quizData)

// Submit answers to Oracle
submitToOracle()

// Display results
displayOracleResults(result)

// Apply visual effects
applyFearLevelStyling(fearLevel)
```

---

## 🎨 Fear Level Classes

```css
body.fear-low      /* 0-30:  Faint glow */
body.fear-medium   /* 31-60: Pulsing red */
body.fear-high     /* 61-85: Fog + flicker */
body.fear-extreme  /* 85+:   Shake + vignette */
```

---

## 📡 API Endpoints

### Start Quiz
```javascript
POST /api/start_quiz
Body: { user_id: "guest" }
Returns: { questions, lore, room, player_profile, oracle_state }
```

### Submit Answers
```javascript
POST /api/submit_answers
Body: { user_id, quiz, answers }
Returns: { score, evaluation, oracle_state, rewards, lore, player_profile }
```

---

## 🎯 Oracle State Object

```javascript
oracleState = {
    fearLevel: 50,          // 0-100
    currentTone: 'neutral',
    userId: 'guest',
    isOracleMode: false
}
```

---

## 🎬 User Journey

```
Click Button → Oracle Chamber → Answer Questions → Oracle Judges
              ↓
        Fear Level Updates → Visual Effects Change → Show Rewards
```

---

## ✨ Key Animations

| Element | Animation | Duration |
|---------|-----------|----------|
| Oracle text | Fade in + slide up | 2s |
| Reward popup | Scale + bounce | 1.5s |
| Fear meter | Width transition | 1s |
| Fear effects | Various | Continuous |

---

## 🐛 Quick Debug

```javascript
// In browser console:

// Check Oracle state
console.log(oracleState);

// Check current quiz
console.log(currentQuiz);

// Test fear effects
applyFearLevelStyling(95);

// Check if functions exist
console.log(typeof startOracleQuiz);
```

---

## 📊 Data Flow

```
startOracleQuiz()
    ↓ POST /api/start_quiz
    ↓ Receive quiz data
displayOracleQuiz()
    ↓ User answers
showQuizResults()
    ↓ (if Oracle mode)
submitToOracle()
    ↓ POST /api/submit_answers
    ↓ Receive evaluation
displayOracleResults()
    ↓ Apply fear styling
    ↓ Show animations
```

---

## 🎨 CSS Keyframes

```css
@keyframes oracleFadeIn      /* Oracle text fade */
@keyframes rewardFadeIn      /* Reward popup */
@keyframes fearPulseMedium   /* Pulsing background */
@keyframes fearFlicker       /* Screen flicker */
@keyframes fearShake         /* Screen shake */
@keyframes bloodPulseExtreme /* Blood pulse */
```

---

## 🧪 Testing Commands

```bash
# Test endpoints
python test_oracle_integration.py

# Start server
python horror.py

# OR
START_ORACLE.bat
```

---

## 📚 Documentation

- **README_ORACLE_INTEGRATION.md** - Start here
- **TESTING_GUIDE.md** - Visual testing
- **ORACLE_ENGINE_FRONTEND_INTEGRATION.md** - Technical details
- **INTEGRATION_SUMMARY.md** - Summary of changes

---

## 🎭 Oracle Behavior

| Fear Level | Oracle Mood | Difficulty |
|-----------|-------------|-----------|
| 0-30 | Pleased/Suspicious | May increase |
| 31-60 | Neutral/Mocking | Balanced |
| 61-85 | Amused/Disappointed | Variable |
| 85+ | Satisfied/Cruel | Variable |

---

## 🔑 Key Code Snippets

### Trigger Oracle Quiz
```javascript
function startOracleQuiz() {
    oracleState.isOracleMode = true;
    // Fetch from /api/start_quiz
    // Display quiz with displayOracleQuiz()
}
```

### Apply Fear Effects
```javascript
function applyFearLevelStyling(fearLevel) {
    body.classList.remove('fear-low', 'fear-medium', 'fear-high', 'fear-extreme');
    if (fearLevel <= 30) body.classList.add('fear-low');
    else if (fearLevel <= 60) body.classList.add('fear-medium');
    else if (fearLevel <= 85) body.classList.add('fear-high');
    else body.classList.add('fear-extreme');
}
```

### Check Oracle Mode
```javascript
if (oracleState.isOracleMode && currentQuiz.oracleData) {
    await submitToOracle();
}
```

---

## 🎬 Visual Checklist

When testing, look for:
- ✅ Oracle chamber appears
- ✅ Lore whispers display
- ✅ Fear meter shows and updates
- ✅ Oracle text fades in (2s)
- ✅ Background changes with fear
- ✅ Rewards popup if earned
- ✅ Smooth animations
- ✅ Proper cleanup on close

---

## 🚨 Common Issues

| Issue | Fix |
|-------|-----|
| Button doesn't work | Check console for errors |
| No reaction text | Verify API response in Network tab |
| No visual effects | Test `applyFearLevelStyling(95)` |
| Quiz won't load | Check Flask is running |

---

## 🎯 Success Criteria

✅ Quiz loads from Oracle Engine  
✅ Oracle reacts emotionally  
✅ Fear meter updates  
✅ Visual effects work  
✅ Animations smooth  
✅ No console errors  

---

## 📞 Help

1. Check browser console (F12)
2. Check Flask logs
3. Run `test_oracle_integration.py`
4. Review **TESTING_GUIDE.md**

---

**Quick Test:**
```javascript
// In console:
startOracleQuiz();
```

**Should display Oracle's chamber immediately.**

---

**Status:** ✅ READY

**Version:** 1.0

🩸 **Face Your Nightmares** 🩸


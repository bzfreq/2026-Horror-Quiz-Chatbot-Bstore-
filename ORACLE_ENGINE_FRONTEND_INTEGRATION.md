# Horror Oracle - Frontend Integration Complete

## 🎭 Overview
The Oracle Engine has been fully integrated into the frontend! The Horror Oracle now delivers an immersive, dynamic quiz experience with real-time reactions, atmospheric effects, and fear-based visual feedback.

## ✅ What Was Implemented

### 1. **Oracle Engine API Integration**
- ✅ Connected `startOracleQuiz()` to `/api/start_quiz` endpoint
- ✅ Connected `submitToOracle()` to `/api/submit_answers` endpoint
- ✅ JSON parsing for quiz data, reactions, rewards, and fear levels
- ✅ Proper error handling and fallback messages

### 2. **Dynamic DOM Updates**
- ✅ Created `oracle-reaction` box that displays the Oracle's emotional response
- ✅ Created `fear-meter` visualization showing current fear level
- ✅ Real-time updates after quiz submission
- ✅ Reward popups with lore fragments
- ✅ Atmospheric lore whispers throughout the experience

### 3. **Fear Level Visual Effects**
Four distinct fear level ranges with escalating intensity:

#### **Fear Level 0-30** (Faint Red Glow)
- Subtle red ambient glow
- Minimal visual interference
- Perfect for confident players

#### **Fear Level 31-60** (Pulsing Red Light)
- Breathing red pulse effect
- Moderate atmospheric pressure
- Background intensifies

#### **Fear Level 61-85** (Fog & Screen Flicker)
- Screen flicker effects
- Animated fog overlay
- Radial gradient vignette
- Growing sense of dread

#### **Fear Level 85+** (Heavy Vignette & Intense Effects)
- Screen shake animation
- Blood pulse overlay
- Heavy vignette darkening edges
- Saturated red color grading
- Maximum atmospheric horror

### 4. **Smooth Animations**
- ✅ 2-second fade-in for Oracle's reaction text (`oracleFadeIn`)
- ✅ 1.5-second reward popup animation (`rewardFadeIn`)
- ✅ Smooth fear meter transitions (1s ease)
- ✅ Button hover effects with scale and glow

### 5. **State Management**
- ✅ `oracleState` object tracks fear level, user ID, and Oracle mode
- ✅ Proper cleanup when closing quiz modal
- ✅ Fear level persists across questions
- ✅ Reset to defaults when exiting

## 🎮 How to Test

### Step 1: Start the Backend
```bash
# In the project root
python horror.py
```
Flask should start on `http://localhost:5000`

### Step 2: Open the Site
Navigate to `http://localhost:5000` in your browser

### Step 3: Click "Face Your Nightmares"
The button in the top header now triggers the Oracle Engine

### Step 4: Observe the Experience

**On Quiz Start:**
- Oracle's chamber/room title appears
- Atmospheric intro text
- Lore whispers (if generated)
- Fear meter displays starting at 50%
- "BEGIN THE TRIAL" button

**During Questions:**
- Standard quiz interface
- Questions from Oracle Engine
- Answer selection

**After Submission:**
- **Score Display:** Shows your score and percentage
- **Oracle Reaction:** Fades in over 2 seconds with emotional response
- **Fear Level Update:** Meter animates to new level
- **Visual Effects:** Background changes based on fear level
- **Rewards:** Popup appears if earned (with lore fragment)
- **Lore Whispers:** Transition text from the Lore Whisperer
- **Next Trial Button:** Continue to next Oracle quiz

### Step 5: Test Different Fear Levels
To test fear effects, you can manually trigger them in browser console:
```javascript
// In browser console:
applyFearLevelStyling(25);  // Low fear
applyFearLevelStyling(45);  // Medium fear
applyFearLevelStyling(75);  // High fear
applyFearLevelStyling(95);  // Extreme fear
```

## 📋 Key Functions Added

### JavaScript Functions (`script-js-combined.js`)

1. **`startOracleQuiz()`**
   - Calls `/api/start_quiz` endpoint
   - Sets up Oracle state
   - Displays quiz with atmospheric intro

2. **`displayOracleQuiz(quizData)`**
   - Renders Oracle's chamber
   - Shows lore and intro
   - Creates fear meter
   - Displays "BEGIN THE TRIAL" button

3. **`submitToOracle()`**
   - Packages answers
   - Calls `/api/submit_answers` endpoint
   - Processes Oracle's evaluation

4. **`displayOracleResults(result)`**
   - Shows score
   - Displays Oracle's reaction with fade-in
   - Renders rewards and lore
   - Updates fear meter
   - Applies visual effects

5. **`applyFearLevelStyling(fearLevel)`**
   - Removes old fear classes
   - Applies new class based on level
   - Triggers CSS animations

6. **`showErrorMessage(message)`**
   - Displays error in modal
   - Provides close button

### Modified Functions

1. **`showQuizResults()`**
   - Now checks if in Oracle mode
   - Routes to `submitToOracle()` if true
   - Falls back to old quiz system otherwise

2. **`closeBloodQuiz()`**
   - Resets Oracle state
   - Removes fear level styling
   - Cleans up quiz data

## 🎨 CSS Classes Added

- `.fear-low` - Faint red glow (0-30%)
- `.fear-medium` - Pulsing red light (31-60%)
- `.fear-high` - Fog & flicker (61-85%)
- `.fear-extreme` - Heavy vignette (85%+)
- `@keyframes oracleFadeIn` - Oracle text animation
- `@keyframes rewardFadeIn` - Reward popup animation
- Various fear-specific animations (shake, pulse, flicker, fog)

## 🔧 Technical Details

### Data Flow
```
User clicks "Face Your Nightmares"
    ↓
startOracleQuiz()
    ↓
POST /api/start_quiz
    ↓
Receive quiz data (questions, lore, profile)
    ↓
displayOracleQuiz()
    ↓
User answers questions
    ↓
showQuizResults() → submitToOracle()
    ↓
POST /api/submit_answers
    ↓
Receive evaluation (score, reaction, rewards, fear_level)
    ↓
displayOracleResults()
    ↓
Apply fear styling + show animations
```

### Oracle State Object
```javascript
oracleState = {
    fearLevel: 50,          // Current fear level (0-100)
    currentTone: 'neutral', // Oracle's emotional tone
    userId: 'guest',        // User identifier
    isOracleMode: false     // Flag for Oracle Engine mode
}
```

### Quiz Data Structure
```javascript
currentQuiz = {
    questions: [],        // Question array
    currentQuestion: 0,   // Current index
    score: 0,            // Running score
    answers: [],         // Answer history
    oracleData: null,    // Full Oracle response
    // ... other fields
}
```

## 🎬 Result
The Horror Oracle is now a living, breathing entity that:
- **Reacts** to player performance emotionally
- **Adapts** difficulty and tone based on history
- **Rewards** with lore and relics
- **Intimidates** through escalating fear effects
- **Immerses** players in atmospheric horror cinema

The system creates a feedback loop:
```
Performance → Oracle Reaction → Fear Level → Visual Effects → Player Experience
```

## 🚀 Next Steps (Optional Enhancements)

1. **Sound Effects**: Add heartbeat sound at fear level 85+
2. **Particle Effects**: Blood drips or mist particles
3. **Haptic Feedback**: Vibration on mobile devices
4. **Progress Tracking**: Visual history of fear levels
5. **Achievements**: Unlock badges based on Oracle trials

## 📞 Support

If the Oracle isn't responding:
1. Check Flask is running on port 5000
2. Check browser console for errors
3. Verify `/api/start_quiz` and `/api/submit_answers` endpoints work
4. Ensure Oracle Engine backend is properly configured

---

**Status**: ✅ **FULLY OPERATIONAL**

The Oracle awaits... Face Your Nightmares. 🩸


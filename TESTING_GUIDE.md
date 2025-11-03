# 🎮 Horror Oracle - Visual Testing Guide

## Quick Test Procedure

### Step 1: Start the Server
```bash
# Option A: Use the batch file
START_ORACLE.bat

# Option B: Run Python directly
python horror.py
```

Wait for Flask to show:
```
 * Running on http://127.0.0.1:5000
```

---

### Step 2: Open Browser
Navigate to: `http://localhost:5000`

---

### Step 3: Visual Validation Checklist

#### ✅ **Initial Load**
- [ ] Page loads with dark horror theme
- [ ] "Horror Oracle" logo visible in header
- [ ] "Face Your Nightmares" button visible in header
- [ ] Button has red glow effect

---

#### ✅ **Click "Face Your Nightmares"**

**Expected Behavior:**
1. Quiz modal appears immediately
2. No slideshow (Oracle mode skips it)
3. Modal displays Oracle's chamber

**What You Should See:**
```
╔══════════════════════════════════════╗
║   THE FIRST CHAMBER                  ║
║   (in red glowing horror font)       ║
║                                      ║
║   The Oracle awaits your challenge...║
║   [Intro text appears here]          ║
║                                      ║
║   📜 Lore whisper appears if any     ║
║   (in italic, left-bordered)         ║
║                                      ║
║   FEAR LEVEL                         ║
║   [████████████░░░░░░░░] 50%        ║
║                                      ║
║   [ 🩸 BEGIN THE TRIAL 🩸 ]         ║
║                                      ║
╚══════════════════════════════════════╝
```

**Validation:**
- [ ] Chamber/room title appears in red
- [ ] Intro text is visible
- [ ] Fear meter shows 50%
- [ ] "BEGIN THE TRIAL" button is present
- [ ] Lore whisper may appear (italicized)

---

#### ✅ **Click "BEGIN THE TRIAL"**

**Expected Behavior:**
Questions appear one at a time

**What You Should See:**
```
╔══════════════════════════════════════╗
║   Question 1 of 5                    ║
║                                      ║
║   [Question text appears here]       ║
║                                      ║
║   ○ Answer option A                  ║
║   ○ Answer option B                  ║
║   ○ Answer option C                  ║
║   ○ Answer option D                  ║
║                                      ║
╚══════════════════════════════════════╝
```

**Validation:**
- [ ] Questions appear cleanly
- [ ] Answer options are clickable
- [ ] Progress indicator shows (1 of 5, 2 of 5, etc.)

---

#### ✅ **Answer All Questions**

After the last question is answered...

**Expected Behavior:**
1. Brief loading moment (< 1 second)
2. Oracle evaluates your answers
3. Results screen appears

---

#### ✅ **Results Screen - THE BIG MOMENT**

**What You Should See:**

```
╔══════════════════════════════════════╗
║                                      ║
║            4/5                       ║
║         (huge red text)              ║
║                                      ║
║         80% Correct                  ║
║                                      ║
║   ┌──────────────────────────────┐  ║
║   │  THE ORACLE SPEAKS:          │  ║
║   │                              │  ║
║   │  [Oracle's emotional         │  ║
║   │   reaction text fades in     │  ║
║   │   over 2 seconds]            │  ║
║   │                              │  ║
║   │  [Atmospheric message]       │  ║
║   └──────────────────────────────┘  ║
║                                      ║
║   ┌──────────────────────────────┐  ║
║   │  ✨ [REWARD NAME] ✨         │  ║
║   │                              │  ║
║   │  [Reward description]        │  ║
║   │                              │  ║
║   │  [Lore fragment if present]  │  ║
║   └──────────────────────────────┘  ║
║                                      ║
║   📜 "[Lore whisper]"               ║
║                                      ║
║   FEAR LEVEL                         ║
║   [████████████████░░░░] 75%        ║
║   (animated transition)              ║
║                                      ║
║   [ 🔮 NEXT TRIAL ]  [ Return ]     ║
║                                      ║
╚══════════════════════════════════════╝
```

**Validation Checklist:**

**Score Display:**
- [ ] Score shows as large number (e.g., "4/5")
- [ ] Percentage appears below (e.g., "80%")

**Oracle's Reaction Box:**
- [ ] Box appears with red border
- [ ] "THE ORACLE SPEAKS:" header visible
- [ ] Oracle's text **fades in over 2 seconds** ← KEY ANIMATION
- [ ] Atmospheric message may appear below

**Reward Popup (if earned):**
- [ ] Golden border box appears
- [ ] Reward name with sparkle emojis (✨)
- [ ] Reward description text
- [ ] Lore fragment (if present)
- [ ] Popup has scale animation

**Lore Whisper:**
- [ ] Appears in italic text
- [ ] Has left border (red line)
- [ ] Contains transition text

**Fear Meter:**
- [ ] Shows new fear level
- [ ] **Bar animates smoothly** over 1 second ← KEY ANIMATION
- [ ] Percentage updates

**Background Effects:**
- [ ] Check for visual changes based on fear level (see below)

**Buttons:**
- [ ] "NEXT TRIAL" button present
- [ ] "Return to Oracle" button present
- [ ] Both have hover effects (scale + glow)

---

### Step 4: Test Fear Level Effects

The most impressive part! Background should change based on fear level.

#### **Test Method 1: Play Multiple Quizzes**
Click "NEXT TRIAL" repeatedly and get different scores:
- Get 5/5 perfect → fear level drops
- Get 0/5 terrible → fear level rises

#### **Test Method 2: Manual Testing (Browser Console)**
Open browser console (F12) and type:

```javascript
// Test Low Fear (0-30)
applyFearLevelStyling(25);

// Wait 3 seconds, then test Medium Fear (31-60)
applyFearLevelStyling(45);

// Wait 3 seconds, then test High Fear (61-85)
applyFearLevelStyling(75);

// Wait 3 seconds, then test Extreme Fear (85+)
applyFearLevelStyling(95);
```

---

### ✅ Fear Level Visual Validation

#### **Fear Level 0-30: Faint Red Glow**
**What to look for:**
- [ ] Subtle red ambient glow around screen edges
- [ ] Very minimal visual interference
- [ ] Almost normal viewing experience
- [ ] Slight red box-shadow on body

**Effect Intensity:** ⭐ (1/5)

---

#### **Fear Level 31-60: Pulsing Red Light**
**What to look for:**
- [ ] Red glow **pulses** (breathes in and out)
- [ ] Pulse cycle is about 2-3 seconds
- [ ] Moderate atmospheric pressure
- [ ] Background darkens slightly
- [ ] Red overlay pulsates

**Effect Intensity:** ⭐⭐⭐ (3/5)

**Animation Check:**
- Watch for smooth brightness changes
- Glow should intensify and fade smoothly

---

#### **Fear Level 61-85: Fog & Screen Flicker**
**What to look for:**
- [ ] **Screen flickers** subtly (very fast)
- [ ] Animated fog/mist effect
- [ ] Radial gradient vignette (dark edges)
- [ ] Background has animated fog movement
- [ ] Red coloring intensifies
- [ ] Brightness changes slightly

**Effect Intensity:** ⭐⭐⭐⭐ (4/5)

**Animation Check:**
- Screen should have brief flicker moments
- Fog should seem to "breathe" and move
- Vignette should pulse
- Overall darker atmosphere

---

#### **Fear Level 85+: Heavy Vignette & Intense Effects**
**What to look for:**
- [ ] **Screen shakes** (subtle left/right movement)
- [ ] Heavy blood-red overlay
- [ ] Strong vignette (very dark edges)
- [ ] Blood pulse effect (red flash)
- [ ] Maximum atmospheric horror
- [ ] Screen edges almost black
- [ ] Red color saturation increased

**Effect Intensity:** ⭐⭐⭐⭐⭐ (5/5)

**Animation Check:**
- Entire page should shake slightly
- Red overlay pulses like a heartbeat
- Vignette creates tunnel vision effect
- Colors should be more saturated
- Maximum immersion

---

### Step 5: Test "NEXT TRIAL" Button

**Expected Behavior:**
1. Click "NEXT TRIAL"
2. New Oracle quiz loads
3. Chamber may change
4. New questions generated
5. Fear level persists from last quiz

**Validation:**
- [ ] Button works
- [ ] New quiz loads
- [ ] Fear level carries over
- [ ] No errors in console

---

### Step 6: Test Close/Exit

**Expected Behavior:**
1. Click "Return to Oracle" or X button
2. Modal closes
3. Fear effects **reset**
4. Oracle state clears

**Validation:**
- [ ] Modal closes cleanly
- [ ] Background returns to normal
- [ ] No lingering fear effects
- [ ] Can reopen quiz successfully

---

## 🐛 Troubleshooting

### Problem: Button doesn't work
**Solution:**
1. Check browser console (F12)
2. Look for JavaScript errors
3. Verify Flask is running

### Problem: No Oracle reaction appears
**Solution:**
1. Check Network tab in DevTools
2. Verify `/api/submit_answers` returns data
3. Check console for errors

### Problem: Fear effects don't show
**Solution:**
1. Try manual test: `applyFearLevelStyling(95)`
2. Check CSS loaded correctly
3. Clear browser cache and reload

### Problem: Animations are choppy
**Solution:**
1. This is normal on slower machines
2. Reduce animation complexity if needed
3. Check browser hardware acceleration

---

## 📊 Success Criteria

Your integration is successful if:

- [x] Quiz loads from Oracle Engine
- [x] Questions appear correctly
- [x] Oracle's reaction fades in (2s)
- [x] Fear meter updates with animation
- [x] Background changes based on fear level
- [x] Rewards display if earned
- [x] Lore whispers appear
- [x] "Next Trial" works
- [x] Modal closes cleanly
- [x] No console errors

---

## 🎬 The Experience

When everything works, you should feel:

1. **Atmosphere** - The Oracle's chamber is foreboding
2. **Tension** - Questions feel meaningful
3. **Judgment** - Oracle's reaction is emotional
4. **Reward** - Lore and relics feel earned
5. **Fear** - Visual effects create unease
6. **Immersion** - The system feels alive

**The Oracle judges. The darkness responds. Your fear is real.**

---

## 📹 Record Your Test

Consider recording a test session to capture:
- Fear effect transitions
- Oracle reaction fade-in
- Reward popup animation
- Fear meter updates
- Overall atmosphere

---

**Happy Testing!** 🩸

*If all checks pass, the integration is complete and working perfectly.*


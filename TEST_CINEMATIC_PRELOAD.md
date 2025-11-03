# 🎬 Testing the Cinematic Preload System

## Quick Test Instructions

### 1. Start the Backend
```bash
python horror.py
```

### 2. Open the Application
- Open `index.html` in your browser
- Or navigate to `http://localhost:5000` (if using Flask to serve)

### 3. Test the Slideshow

#### Click "Face Your Nightmares" button
You should see:

**✅ Expected Behavior:**
1. **Instant slideshow appears** (black screen with first image)
2. **6 horror portraits cycle** (every 2 seconds):
   - The Butcher
   - The Preacher
   - The Doctor
   - Terrified Souls
   - Screams
   - The Risen
3. **Title overlay**: "The Oracle Awakens..." (pulsing red text)
4. **Progress bar** at bottom fills over 10 seconds
5. **After 10 seconds**: Images fade out, "Start Your Trials Now" button appears

#### Click "Start Your Trials Now"
You should see:
1. **Button click** → Slideshow overlay fades out
2. **Quiz modal appears INSTANTLY** (no loading delay)
3. **First question** is already loaded and ready

---

## 🔍 Console Logs to Verify

Open browser console (F12) and look for these logs:

### When clicking "Face Your Nightmares":
```
🔮 Starting Oracle Quiz with Cinematic Preload...
[DEBUG] 🟢 Face Your Nightmares button disabled and marked as clicked
🎬🔮 PARALLEL EXECUTION: Starting slideshow + preloading quiz...
🎬 Starting cinematic slideshow...
⏳ PRELOADING quiz data in background...
🖼️ Slideshow: Image 1/6
🖼️ Slideshow: Image 2/6
🖼️ Slideshow: Image 3/6
🖼️ Slideshow: Image 4/6
🖼️ Slideshow: Image 5/6
🖼️ Slideshow: Image 6/6
✅ PRELOAD COMPLETE in 3.45s  (timing will vary)
✅ Preloaded Questions: 3
🎬 Slideshow complete
🔘 Showing Start Your Trials Now button...
```

### When clicking "Start Your Trials Now":
```
🚀 Launching preloaded quiz...
✅ Using preloaded quiz data (instant load)
🎮 Displaying preloaded quiz...
✅ Mapped questions to frontend format: [...]
```

---

## ⚡ Performance Check

### Timing Expectations:
- **Preload time**: 3-6 seconds (depends on backend/LLM speed)
- **Slideshow duration**: Exactly 10 seconds
- **Safety margin**: 4-7 seconds (preload finishes before slideshow)
- **Quiz launch after button click**: <1 second (instant)

### Verify Performance:
1. Note the `PRELOAD COMPLETE` time in console
2. It should be **less than 10 seconds** (before slideshow ends)
3. Quiz should appear **instantly** when button is clicked

---

## 🎨 Visual Check

### Slideshow Should Have:
- ✅ Black-and-white (grayscale) images
- ✅ Slow zoom effect (images slowly scale up)
- ✅ Smooth cross-fade between images
- ✅ Dark vignette around edges
- ✅ Red glowing title text at top
- ✅ Red progress bar at bottom that fills up

### "Start Your Trials Now" Button Should:
- ✅ Appear centered after slideshow
- ✅ Have horror font (Nosifer)
- ✅ Have red gradient background
- ✅ Pulse/glow effect
- ✅ Scale up on hover
- ✅ Scale down when clicked

---

## 🐛 Troubleshooting

### Issue: Slideshow doesn't appear
**Check:**
- Browser console for errors
- Images exist in root directory
- `#introSlideshow` element exists in HTML

### Issue: Preload takes too long (>10s)
**Check:**
- Backend is running
- Oracle Engine is properly initialized
- Network connection is stable
**Fallback:**
- System will show loading spinner when button clicked
- Will fetch quiz data on-demand

### Issue: Quiz doesn't load when button clicked
**Check:**
- Console for `preloadedQuizData` value
- If null, fallback should trigger
- Backend `/api/start_quiz` endpoint is working

### Issue: Images not showing
**Check:**
- All 6 images exist in root directory:
  - `butcher.png`
  - `preecher.png`
  - `doctormad.png`
  - `terrifiedwomen.png`
  - `screams.png`
  - `zombsing.png`

---

## 🎯 Success Criteria

✅ **Slideshow starts immediately** (no delay)  
✅ **All 6 images display** in black-and-white  
✅ **Smooth cross-fade** transitions  
✅ **Progress bar fills** over 10 seconds  
✅ **"Start Your Trials Now" button appears** after slideshow  
✅ **Quiz loads instantly** when button clicked (<1s)  
✅ **No loading spinners** or blank screens  
✅ **Console logs show successful preload**  

---

## 📊 Expected Timeline

```
0s:  Click "Face Your Nightmares"
     → Slideshow starts
     → Preload begins in background

2s:  Image 2 (The Preacher)
4s:  Image 3 (The Doctor)
     → Preload likely complete by now
6s:  Image 4 (Terrified Souls)
8s:  Image 5 (Screams)
10s: Image 6 (The Risen)
     → Slideshow fades out
     → "Start Your Trials Now" button appears

11s: User clicks button
     → Quiz appears INSTANTLY (using preloaded data)
```

---

## 🎬 Advanced Testing

### Test Slow Network
1. Open DevTools → Network tab
2. Throttle to "Slow 3G"
3. Click "Face Your Nightmares"
4. Preload might take longer, but slideshow keeps running
5. If preload not ready by 10s, button will show loading spinner

### Test Backend Failure
1. Stop the backend
2. Click "Face Your Nightmares"
3. Slideshow runs normally
4. Preload fails (check console)
5. When button clicked, fallback fetch occurs
6. User sees "connecting to oracle" message

### Test Multiple Launches
1. Complete a quiz
2. Start another quiz
3. Slideshow should run again
4. Preload should work for second quiz too

---

## 🎭 Enjoy the Cinematic Experience!

The slideshow adds a professional, cinematic feel to the Horror Oracle. It transforms a boring loading screen into an atmospheric intro that sets the mood for the quiz experience.

**Status**: ✅ Ready to Test



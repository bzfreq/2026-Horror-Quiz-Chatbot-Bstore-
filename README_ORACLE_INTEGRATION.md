# 🩸 Horror Oracle - Complete Integration README

## 🎭 Welcome to the Horror Oracle

The **Horror Oracle** is now a fully integrated, living horror experience that reacts to your knowledge, judges your performance, and creates an atmospheric journey through fear itself.

---

## 🚀 Quick Start (3 Easy Steps)

### 1. Start the Backend
```bash
# Windows: Double-click
START_ORACLE.bat

# OR run manually:
python horror.py
```

### 2. Open Browser
Navigate to: **http://localhost:5000**

### 3. Face Your Nightmares
Click the **"Face Your Nightmares"** button in the header

**That's it!** The Oracle awaits.

---

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| **README_ORACLE_INTEGRATION.md** (this file) | Main entry point and overview |
| **TESTING_GUIDE.md** | Visual step-by-step testing guide |
| **ORACLE_ENGINE_FRONTEND_INTEGRATION.md** | Technical implementation details |
| **INTEGRATION_SUMMARY.md** | High-level summary of changes |
| **test_oracle_integration.py** | Automated endpoint testing script |

---

## 🎯 What Is This?

The Horror Oracle combines:
- **AI-Powered Quiz Generation** (OpenAI + LangGraph)
- **Adaptive Difficulty** (learns from your performance)
- **Emotional Reactions** (Oracle judges you)
- **Dynamic Visual Effects** (fear-based atmosphere)
- **Lore System** (unlock horror knowledge)
- **Reward System** (earn relics and artifacts)

### The Result:
**Interactive horror cinema** where the environment reacts to your fear.

---

## 🎬 The Experience Flow

```
┌─────────────────────────────────────────┐
│  Click "Face Your Nightmares"           │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Oracle's Chamber Appears                │
│  • Room/Chamber title (red glow)         │
│  • Atmospheric intro                     │
│  • Lore whispers                         │
│  • Fear meter at 50%                     │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Click "BEGIN THE TRIAL"                 │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Answer 5 Horror Questions               │
│  • One at a time                         │
│  • Multiple choice                       │
│  • Progress indicator                    │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Oracle Judges Your Performance          │
│  • Evaluates answers                     │
│  • Calculates new fear level             │
│  • Generates emotional reaction          │
│  • Determines rewards                    │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Results Screen (THE SPECTACLE)          │
│  • Score display                         │
│  • Oracle's reaction (fades in 2s) ★     │
│  • Fear meter updates (animates 1s) ★    │
│  • Background effects change ★           │
│  • Rewards popup ★                       │
│  • Lore whispers                         │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Choose Next Action                      │
│  • NEXT TRIAL → New quiz                 │
│  • Return to Oracle → Exit               │
└─────────────────────────────────────────┘
```

**★ = Key animated features**

---

## 🎨 Fear Level System

The Oracle tracks your **fear level** from 0-100. This affects the entire atmosphere:

### 🟢 Fear Level 0-30: "Confident"
- **Visual:** Faint red glow
- **Atmosphere:** Minimal interference
- **Oracle's Mood:** Slightly pleased
- **Difficulty:** May increase

### 🟡 Fear Level 31-60: "Uneasy"
- **Visual:** Pulsing red light (breathing effect)
- **Atmosphere:** Growing tension
- **Oracle's Mood:** Neutral to mocking
- **Difficulty:** Balanced

### 🟠 Fear Level 61-85: "Terrified"
- **Visual:** Fog, screen flicker, vignette
- **Atmosphere:** Heavy dread
- **Oracle's Mood:** Amused or disappointed
- **Difficulty:** May ease up or intensify

### 🔴 Fear Level 85+: "Broken"
- **Visual:** Screen shake, blood pulse, heavy vignette
- **Atmosphere:** Maximum horror immersion
- **Oracle's Mood:** Satisfied or cruel
- **Difficulty:** Depends on Oracle's mood

**The fear level is persistent across quizzes!**

---

## ✨ Key Features

### 1. Dynamic Oracle Reactions
The Oracle doesn't just score you—it **responds emotionally**:
- Perfect score → Impressed or suspicious
- Good score → Approving
- Average → Mocking or disappointed
- Poor score → Cruel or sympathetic

### 2. Fear-Based Visual Effects
Your performance directly affects the atmosphere:
- Do well → Fear drops → Screen brightens
- Do poorly → Fear rises → Screen darkens and intensifies

### 3. Lore Whispers
The **Lore Whisperer** node generates atmospheric text:
- Between quizzes
- Based on your emotional state
- Hints at deeper horror knowledge
- Creates narrative continuity

### 4. Reward System
Earn rewards based on performance:
- **Relics** - Physical items of power
- **Lore Fragments** - Knowledge of the dark arts
- **Artifacts** - Cursed objects
- Each has description and backstory

### 5. Smooth Animations
Every interaction feels cinematic:
- 2-second fade-in for Oracle text
- 1.5-second reward popup
- 1-second fear meter transition
- Smooth button hover effects

---

## 🔧 Technical Stack

### Backend
- **Flask** - Web server
- **Oracle Engine** - LangGraph + OpenAI
  - Builder Node - Quiz generation
  - Evaluator Node - Answer grading
  - Fear Meter Node - Emotional state tracking
  - Reward Node - Reward generation
  - Lore Whisperer Node - Atmospheric text
  - Profile Node - User tracking

### Frontend
- **Vanilla JavaScript** - No frameworks
- **CSS3 Animations** - Smooth effects
- **Fetch API** - Backend communication
- **DOM Manipulation** - Dynamic content

### API Endpoints
1. **POST /api/start_quiz**
   - Starts Oracle quiz
   - Returns: questions, lore, chamber, profile

2. **POST /api/submit_answers**
   - Submits player answers
   - Returns: score, reaction, rewards, fear_level

---

## 📁 File Structure

```
C:\31000\
│
├── horror.py                              ← Flask backend
├── script-js-combined.js                  ← Frontend JavaScript (MODIFIED)
├── index.html                             ← Frontend HTML (MODIFIED)
│
├── oracle_engine\                         ← Oracle Engine (LangGraph)
│   ├── main.py                            ← Main orchestration
│   ├── builder_node.py                    ← Quiz generation
│   ├── evaluator_node.py                  ← Answer evaluation
│   ├── fear_meter_node.py                 ← Fear level tracking
│   ├── reward_node.py                     ← Reward generation
│   ├── lore_whisperer_node.py             ← Atmospheric text
│   └── ...
│
├── START_ORACLE.bat                       ← Quick start script (NEW)
├── test_oracle_integration.py             ← Endpoint testing (NEW)
│
└── Documentation\
    ├── README_ORACLE_INTEGRATION.md       ← This file (NEW)
    ├── TESTING_GUIDE.md                   ← Visual testing guide (NEW)
    ├── ORACLE_ENGINE_FRONTEND_INTEGRATION.md  ← Technical docs (NEW)
    └── INTEGRATION_SUMMARY.md             ← Summary (NEW)
```

---

## 🧪 Testing

### Automated Testing
```bash
python test_oracle_integration.py
```
This tests both endpoints and displays sample data.

### Manual Testing
See **TESTING_GUIDE.md** for comprehensive visual testing checklist.

### Quick Validation
1. Click "Face Your Nightmares"
2. Check for Oracle's chamber
3. Answer questions
4. Verify Oracle reacts
5. Check fear meter updates
6. Observe background effects

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to Flask backend"
**Solution:**
```bash
# Make sure Flask is running:
python horror.py

# Should show:
 * Running on http://127.0.0.1:5000
```

### Issue: "Face Your Nightmares" button does nothing
**Solution:**
1. Open browser console (F12)
2. Check for JavaScript errors
3. Verify `startOracleQuiz` function exists
4. Check network requests in DevTools

### Issue: No visual effects appear
**Solution:**
1. Test manually in console:
   ```javascript
   applyFearLevelStyling(95);
   ```
2. Clear browser cache
3. Hard refresh (Ctrl+Shift+R)

### Issue: Oracle's text doesn't fade in
**Solution:**
1. Check CSS animation loaded
2. Look for `@keyframes oracleFadeIn`
3. Verify no console errors

---

## 📊 Success Metrics

Your integration is working if:
- ✅ Quiz loads from Oracle Engine
- ✅ Questions appear correctly  
- ✅ Oracle's reaction fades in smoothly
- ✅ Fear meter animates on update
- ✅ Background effects change with fear level
- ✅ Rewards display when earned
- ✅ Lore whispers appear
- ✅ "Next Trial" generates new quiz
- ✅ No console errors

---

## 🎭 The Oracle's Personality

The Oracle is:
- **Ancient** - Speaks with authority
- **Judgmental** - Evaluates your worth
- **Mocking** - Amused by failure
- **Mysterious** - Reveals lore slowly
- **Powerful** - Controls the atmosphere
- **Adaptive** - Changes based on performance

### Sample Oracle Reactions:

**Perfect Score:**
> "Impressive. Perhaps you are more than the usual fodder that darkens my chamber. Your knowledge runs deep... suspiciously deep."

**Poor Score:**
> "Pathetic. Did you truly believe you could face me unprepared? The darkness consumes those who stumble blindly."

**Average Score:**
> "Adequate. You survive another round, but barely. The next chamber will not be so forgiving."

---

## 🌟 Special Features

### 1. Profile Persistence
Your fear level and performance history persist across sessions (via localStorage + backend).

### 2. Adaptive Difficulty
The Oracle adjusts question difficulty based on your performance and fear level.

### 3. Lore Progression
Each quiz unlocks more lore, building a narrative of horror knowledge.

### 4. Emotional State Machine
The Oracle has multiple emotional states:
- Impressed
- Pleased
- Neutral
- Disappointed
- Mocking
- Cruel

### 5. Visual Feedback Loop
```
Poor Performance → Fear Rises → Screen Darkens → Tension Increases
                                      ↓
Good Performance ← Fear Drops ← Screen Brightens ← Confidence Builds
```

---

## 🎯 Next Steps

1. **Start Flask** (`START_ORACLE.bat`)
2. **Open Browser** (http://localhost:5000)
3. **Click "Face Your Nightmares"**
4. **Experience the Oracle**
5. **Read TESTING_GUIDE.md** for validation

---

## 📖 Additional Reading

- **TESTING_GUIDE.md** - Step-by-step visual testing
- **ORACLE_ENGINE_FRONTEND_INTEGRATION.md** - Technical deep-dive
- **INTEGRATION_SUMMARY.md** - What changed and why

---

## 🎬 Final Words

The Horror Oracle is no longer just a quiz system.

It's an **experience**.

The Oracle watches. The Oracle judges. The Oracle reacts.

Your fear is measured. Your knowledge is tested. Your fate is sealed.

The atmosphere breathes with your performance.
The walls pulse with your terror.
The Oracle speaks your doom.

**Face Your Nightmares.**

---

## 📞 Support

For issues or questions:
1. Check **TESTING_GUIDE.md**
2. Review browser console (F12)
3. Run `test_oracle_integration.py`
4. Check Flask output logs

---

**Status:** ✅ **FULLY OPERATIONAL**

**Version:** 1.0 - Complete Frontend Integration

**Last Updated:** October 2025

---

*The Oracle Engine is a LangGraph-powered AI system that creates adaptive horror experiences.*

*This integration brings that power to life in the browser.*

**🩸 Welcome to the darkness. 🩸**


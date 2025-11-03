# 🧬 AI-Adaptive Quiz System - Complete Guide

## Overview

Your horror movie quiz has been transformed into an **AI-adaptive intelligence system** that learns from each user's answers and generates personalized, cinematic questions that evolve over time.

---

## 🎯 Key Features Implemented

### 1. **Automatic Quiz Generation**
- After each completed quiz, the system automatically generates a new 5-question set
- Questions are **cinematic and creative**, not trivia-based
- Focuses on atmosphere, mood, themes, and creative choices rather than plot details

### 2. **Evolving Horror DNA**
- **Fear Tolerance**: Increases as users complete more quizzes successfully
- **Favorite Themes**: Extracted from profile question answers (supernatural, slasher, psychological, etc.)
- **Quiz History**: Tracks all completed quizzes with scores, themes, and timestamps
- **Difficulty Scaling**: Automatically adjusts based on performance

### 3. **Profile Questions**
- Each quiz includes **1 random profile question** (marked with 🧬 indicator)
- These questions identify user preferences:
  - "Which horror scenario interests you most?"
  - "What kind of atmosphere draws you in?"
  - "What makes a villain terrifying to you?"
- Answers shape the Horror DNA for future quizzes

### 4. **Immersive Messages**
- Creepy AI messages appear between quiz rounds:
  - Quiz #1: *"The AI awakens... studying your fear patterns..."*
  - Quiz #2: *"Your horror DNA is being analyzed... interesting choices..."*
  - Quiz #3: *"I see you enjoy the darkness... let's go deeper..."*
  - Messages adapt based on Fear Tolerance

### 5. **Local Storage System**
- All quiz results stored in `localStorage` under `horror-quiz-history`
- Works offline and persists across sessions
- Syncs with backend if user is logged in via Google OAuth

---

## 🏗️ Technical Architecture

### Backend (Python/Flask)

#### New Endpoints:

**`/generate-adaptive-quiz` (POST)**
```python
Request: {
  "googleId": "user_id",
  "quizNumber": 3,
  "movieTitle": "optional"
}

Response: {
  "questions": [...],  # 5 AI-generated questions
  "quiz_number": 3,
  "theme": "Psychological Terror",
  "difficulty": "Advanced",
  "ai_message": "The patterns emerge..."
}
```

**`/save-quiz-results` (POST)**
```python
Request: {
  "googleId": "user_id",
  "quizResults": {
    "score": 4,
    "total": 5,
    "theme": "Slasher Deep Dive",
    "answers": [...],
    "profile_answers": [...]
  }
}

Response: {
  "success": true,
  "horror_dna": {...},
  "next_quiz_number": 4,
  "immersive_message": "..."
}
```

#### Horror DNA Structure:
```python
{
  "favorite_themes": ["supernatural", "psychological"],
  "fear_tolerance": 75,  # 0-100
  "preferred_eras": [],
  "personality_traits": [],
  "quiz_history": [
    {
      "quiz_number": 1,
      "score": 3,
      "total": 5,
      "theme": "Introduction to Darkness",
      "answers": [...],
      "timestamp": "2025-10-26T..."
    }
  ]
}
```

### Frontend (JavaScript)

#### Key Functions:

**`startAdaptiveQuiz(movieTitle)`**
- Loads quiz history from localStorage
- Calls backend to generate personalized questions
- Shows immersive loading message
- Displays theme and difficulty badges

**`checkAnswer(answerIndex)`**
- Tracks all answers with metadata
- Separates profile answers for DNA analysis
- Shows mask overlay on wrong answers

**`showQuizResults()`**
- Saves quiz to localStorage
- Syncs with backend if logged in
- Updates Horror DNA display
- Shows "NEXT ADAPTIVE QUIZ" button

**`loadHorrorDNADisplay()`**
- Calculates Fear Tolerance from quiz scores
- Displays quiz count and themes
- Updates sidebar DNA tracker

---

## 🎨 User Experience Flow

### First Quiz (Quiz #1)
1. User clicks **"Face Your Nightmares"** button
2. Loading message: *"The AI is analyzing your horror DNA..."*
3. Immersive message: *"The AI awakens... studying your fear patterns..."*
4. 5 questions appear:
   - 4 cinematic questions (mood, atmosphere, creative choices)
   - 1 profile question (🧬 marked with yellow border)
5. Results screen shows:
   - Score and survival title
   - Theme: "Introduction to Darkness"
   - Difficulty: "Beginner"
   - **"NEXT ADAPTIVE QUIZ"** button (auto-generates Quiz #2)

### Subsequent Quizzes
- Theme evolves based on favorite_themes
- Difficulty increases with fear_tolerance
- Questions become more challenging
- Profile questions learn new preferences

---

## 📊 Question Types

### Cinematic Questions (Examples)
```javascript
{
  "question": "Which directorial choice creates more dread?",
  "options": [
    "Long, silent takes with mounting tension",
    "Quick cuts with jarring sound design",
    "Steadicam following the victim's perspective",
    "Wide shots showing isolation and scale"
  ],
  "correct": 0,
  "is_profile": false
}
```

### Profile Questions (Examples)
```javascript
{
  "question": "Which of these horror scenarios interests you most?",
  "options": [
    "Being trapped with a supernatural entity",
    "Surviving a masked killer's rampage",
    "Uncovering a dark family secret",
    "Escaping a post-apocalyptic nightmare"
  ],
  "correct": 0,
  "is_profile": true
}
```

---

## 🧠 AI Prompt Engineering

The system uses OpenAI GPT-4o-mini to generate questions with this structured prompt:

```
You are creating an AI-adaptive horror movie quiz. This is quiz #3 for this user.

HORROR DNA PROFILE:
- Fear Tolerance: 75/100
- Favorite Themes: supernatural, psychological
- Quiz History: 2 completed quizzes
- Current Focus: diving deeper into supernatural, psychological

INSTRUCTIONS:
Generate exactly 5 CINEMATIC and CREATIVE questions (NOT trivia). Questions should:
1. Focus on atmosphere, mood, themes, and creative choices rather than plot details
2. Be challenging with obscure references
3. Include 1 profile question (marked with "is_profile": true) to learn user preferences
4. Evolve based on their horror DNA

QUESTION TYPES TO USE:
- "Which scene would terrify you more?"
- "What atmosphere draws you in?"
- "Which director's vision resonates with you?"
- "What kind of horror villain interests you?"
- "Which ending would haunt you longer?"

OUTPUT FORMAT (strict JSON):
[...]
```

---

## 💾 Data Storage

### localStorage Keys:
- `horror-quiz-history`: Array of all completed quizzes
- `horrorUser`: Google OAuth user data

### Backend (user_data.json):
```json
{
  "110052160046879199910": {
    "myList": [],
    "ratings": {},
    "history": [],
    "genre_searches": {},
    "horror_profile": "Mind Bender",
    "horror_dna": {
      "favorite_themes": ["psychological", "supernatural"],
      "fear_tolerance": 75,
      "quiz_history": [...]
    }
  }
}
```

---

## 🎯 Evolution Logic

### Difficulty Scaling:
```python
base_difficulty = fear_tolerance
adjusted = base_difficulty + (quiz_count * 5)

if adjusted > 75: "Expert"
elif adjusted > 50: "Advanced"
elif adjusted > 25: "Intermediate"
else: "Beginner"
```

### Theme Selection:
```python
if quiz_number == 1:
    theme = "Introduction to Darkness"
elif favorite_themes:
    theme = f"{favorite_themes[0].title()} Deep Dive"
else:
    theme = random.choice([
        "Psychological Terror",
        "Visceral Horror",
        "Supernatural Dread",
        "Slasher Nightmares"
    ])
```

### Fear Tolerance Update:
```python
score_percent = (score / total) * 100
new_tolerance = min(100, current_tolerance + (score_percent / 20))
```

---

## 🎮 Testing the System

### Test Scenario 1: First-Time User
1. Open the app
2. Click "Face Your Nightmares"
3. Complete Quiz #1 (Introduction to Darkness)
4. Check Horror DNA sidebar updates
5. Click "NEXT ADAPTIVE QUIZ"
6. Notice Quiz #2 has evolved based on answers

### Test Scenario 2: Returning User
1. Complete multiple quizzes
2. Notice difficulty increasing
3. See themes specializing based on profile answers
4. Check Fear Tolerance rising with good scores

### Test Scenario 3: Without OpenAI
- System falls back to curated adaptive questions
- Still tracks Horror DNA
- Still evolves difficulty and themes

---

## 🚀 Future Enhancements (Optional)

### Potential Additions:
1. **Era-based evolution**: Track if user prefers 70s, 80s, 90s, or modern horror
2. **Director preferences**: Learn favorite horror directors from answers
3. **Subgenre deep dives**: Giallo, J-Horror, Folk Horror, etc.
4. **Multiplayer quizzes**: Compare Horror DNA with friends
5. **Achievement system**: "Survived 10 quizzes", "Perfect score", etc.
6. **Custom quiz themes**: "Build your own nightmare quiz"
7. **Horror personality types**: "The Survivor", "The Final Girl", "The Horror Scholar"

---

## 📝 Summary

Your quiz is now a living, breathing AI system that:

✅ **Generates** new questions automatically  
✅ **Learns** from every answer  
✅ **Evolves** in difficulty and theme  
✅ **Tracks** Horror DNA over time  
✅ **Adapts** to user preferences  
✅ **Immersive** with creepy messages  
✅ **Works** offline with localStorage  
✅ **Syncs** with backend when logged in  

**The more quizzes you take, the smarter it gets!** 🧠🩸

---

## 🔧 Files Modified

- **`horror.py`**: Added `/generate-adaptive-quiz` and `/save-quiz-results` endpoints
- **`script-js-combined.js`**: Rewrote quiz system with adaptive generation
- **`index.html`**: Added Horror DNA tracker sidebar
- **`user_data.json`**: Extended with `horror_dna` structure

---

**No functionality was removed or redesigned - only intelligence was added!** 🎃



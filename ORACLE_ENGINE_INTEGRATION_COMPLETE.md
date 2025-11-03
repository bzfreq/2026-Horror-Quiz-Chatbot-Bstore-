# Oracle Engine Integration - Complete

## ✅ Implementation Summary

The Oracle Engine has been fully integrated with the Flask backend. The `/api/start_quiz` and `/api/submit_answers` routes now trigger the complete AI chain.

---

## 🔗 Full Chain Flow

### **Start Quiz Chain** (`/api/start_quiz`)

When a user starts a quiz, the following chain executes:

1. **Builder Node** → Generates 5 horror quiz questions
2. **Profile Node** → Loads or creates user profile
3. **Lore Whisperer** → Generates atmospheric intro text
4. **Fear Meter** → Initializes Oracle's emotional state

**Response includes:**
- Quiz questions with choices and correct answers
- Atmospheric lore and intro text
- Oracle's initial state (tone, emotion, intensity)
- User profile data

---

### **Submit Answers Chain** (`/api/submit_answers`)

When a user submits answers, the following 7-node chain executes:

1. **Evaluator Node** → Scores answers and generates feedback
2. **Reactor (Fear Meter)** → Translates performance into Oracle's emotional response
3. **Reward Node** → Generates rewards based on performance
4. **Profile Node** → Updates user profile with new data
5. **Recommender Node** → Generates personalized movie recommendations
6. **Lore Whisperer** → Creates atmospheric transition text
7. **Fear Meter** → Compiles final Oracle state

**Response includes:**
- Score and detailed feedback for each question
- Oracle's emotional reaction (tone, emotion, intensity)
- Rewards and achievements
- Updated player profile (fear level, confidence, etc.)
- Movie recommendations
- Atmospheric lore for transitions
- Next difficulty and recommended actions

---

## 📡 API Endpoints

### POST `/api/start_quiz`

**Request Body:**
```json
{
  "user_id": "player_123"
}
```

**Response:**
```json
{
  "user_id": "player_123",
  "room": "Chamber of Intermediate",
  "intro": "The air grows cold as you enter...",
  "questions": [
    {
      "question": "In what year did the first slasher...",
      "choices": ["1960 (Psycho)", "1974 (Black Christmas)", ...],
      "correct_answer": "1960 (Psycho)",
      "difficulty": 0.4,
      "tone": "creepy",
      "theme": "general_horror"
    }
  ],
  "theme": "general_horror",
  "difficulty": "intermediate",
  "tone": "creepy",
  "lore": {
    "lore_fragment": {...},
    "atmosphere": {...},
    "oracle_voice": {...}
  },
  "oracle_state": {
    "tone": "neutral",
    "emotion": "indifferent",
    "intensity": 0.5
  },
  "player_profile": {
    "user_id": "player_123",
    "bravery": 50,
    "lore_knowledge": 50,
    "fear_level": 50,
    ...
  }
}
```

---

### POST `/api/submit_answers`

**Request Body:**
```json
{
  "user_id": "player_123",
  "quiz": { /* quiz data from start_quiz */ },
  "answers": {
    "Question 1 text": "Player's choice",
    "Question 2 text": "Player's choice",
    ...
  }
}
```

**Response:**
```json
{
  "user_id": "player_123",
  "score": 3,
  "out_of": 5,
  "accuracy": 0.6,
  "percentage": 60.0,
  
  "evaluation": {
    "grade": "B",
    "verdict": "Your answers echo through empty corridors...",
    "detailed_feedback": [
      {
        "question": "...",
        "player_answer": "...",
        "correct_answer": "...",
        "is_correct": true,
        "comment": "Correct."
      }
    ],
    "oracle_reaction": "Cold fingers trace your spine...",
    "unlocked_lore": null
  },
  
  "oracle_state": {
    "tone": "creepy",
    "emotion": "pleased",
    "intensity": 0.65,
    "next_tone": "approving",
    "atmospheric_message": "The Oracle watches with growing interest...",
    "behavior": {
      "difficulty_adjustment": "advance",
      "reveal_lore": true,
      "mock_intensity": 0.3,
      "rewards_granted": true
    },
    "narrative": {
      "chamber_atmosphere": "Dim candlelight flickers...",
      "oracle_stance": "The Oracle leans closer...",
      "transition_text": "The next chamber beckons..."
    }
  },
  
  "rewards": {
    "rewards": [],
    "unlocks": [],
    "achievements": [],
    "next_challenge": "advance"
  },
  
  "player_profile": {
    "user_id": "player_123",
    "difficulty_level": "intermediate",
    "fear_level": 45,
    "confidence": "improving",
    ...
  },
  
  "recommendations": [],
  
  "lore": {
    "lore_fragment": {
      "text": "Knowledge gleams in the darkness...",
      "style": "dark_wisdom",
      "intensity": 0.65
    },
    "atmosphere": {
      "mood": "mysterious",
      "visual_hints": ["flickering_candles", "shadow_figures"],
      "ambient_sound": "distant_whispers",
      "intensity_level": "medium"
    },
    "oracle_voice": {
      "tone": "pleased",
      "emotion": "pleased",
      "intimacy_level": "approving",
      "volume": "normal"
    }
  },
  
  "next_action": "advance",
  "next_difficulty": "advance"
}
```

---

## 🔧 Changes Made

### 1. **horror.py**
- ✅ Removed duplicate old quiz routes (lines 1137-1382)
- ✅ Kept Oracle Engine routes at `/api/start_quiz` and `/api/submit_answers`
- ✅ Routes now properly call `oracle_engine.main` functions

### 2. **oracle_engine/main.py**
- ✅ Imported all node modules (Builder, Evaluator, Reward, Profile, Recommender, Lore, Fear Meter)
- ✅ Updated `start_first_quiz()` to execute: Builder → Profile → Lore → Fear Meter
- ✅ Updated `evaluate_and_progress()` to execute full 7-node chain
- ✅ Added detailed logging for debugging

---

## 🧪 Testing

A comprehensive integration test was run with the following results:

✅ **Test 1: Start Quiz**
- Successfully generated 5 questions
- Lore and atmosphere created
- Oracle state initialized

✅ **Test 2: Evaluate Answers**
- All 7 nodes executed successfully
- Score calculated correctly
- Oracle emotional response generated
- Profile updated with new fear level
- Lore transition created

**Test Output:**
```
[ORACLE ENGINE] Starting quiz for user: test_user
[1/4] Loading user profile...
[2/4] Generating quiz questions...
[3/4] Whispering lore...
[4/4] Calibrating fear meter...
[OK] Quiz generated | Theme: general_horror | Difficulty: intermediate

[ORACLE ENGINE] Evaluating answers for user: test_user
[1/7] Evaluating answers...
[OK] Score: 1/5 (20.0%)
[2/7] Oracle reacts to performance...
[OK] Oracle Emotion: amused | Tone: mocking
[3/7] Generating rewards...
[4/7] Updating player profile...
[OK] Profile updated | Fear Level: 80
[5/7] Generating movie recommendations...
[6/7] Whispering transition lore...
[7/7] Compiling final state...
[OK] Full chain complete | Next: descend
```

---

## 🎯 Next Steps

To use the Oracle Engine in your application:

1. **Start the Flask server:**
   ```bash
   python horror.py
   ```

2. **Call the start quiz endpoint:**
   ```javascript
   fetch('http://localhost:5000/api/start_quiz', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ user_id: 'player_123' })
   })
   ```

3. **Display the quiz to the user**

4. **Submit answers:**
   ```javascript
   fetch('http://localhost:5000/api/submit_answers', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       user_id: 'player_123',
       quiz: quizData,
       answers: userAnswers
     })
   })
   ```

5. **Display Oracle's reaction, score, and lore**

---

## ⚙️ Configuration

The Oracle Engine works with or without an OpenAI API key:

- **With API Key:** Generates dynamic, AI-powered questions and feedback
- **Without API Key:** Uses curated fallback questions and reactions

Set your API key in `.env`:
```
OPENAI_API_KEY=your_key_here
```

---

## 🩸 Horror Oracle Features

The integrated system provides:

- **Dynamic Question Generation** - AI-crafted horror trivia
- **Emotional Oracle** - Reacts to player performance with personality
- **Fear Meter** - Tracks and adjusts difficulty based on player state
- **Atmospheric Lore** - Immersive narrative between quiz chambers
- **Personalized Rewards** - Achievements and unlocks
- **Profile Evolution** - Player profile grows with each quiz
- **Movie Recommendations** - Tailored to player preferences
- **Multi-Toned Reactions** - Creepy, mocking, ancient, whispered, grim, or playful

---

**Status:** ✅ **FULLY OPERATIONAL**

The Oracle Engine is now ready to deliver a complete horror quiz experience with atmospheric AI-driven interactions!


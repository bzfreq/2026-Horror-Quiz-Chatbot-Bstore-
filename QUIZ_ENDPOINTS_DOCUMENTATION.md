# Quiz Endpoints Documentation

## Overview
Two new quiz endpoints have been added to the Horror Oracle Flask backend to enable the quiz chamber system.

---

## Endpoints

### 1. **POST /api/start_quiz**

**Purpose:** Generate a new 5-question horror quiz with chamber theme.

**Request Body:**
```json
{
  "googleId": "user123" (optional),
  "chamber_level": 1 (default: 1)
}
```

**Response Format:**
```json
{
  "chamber_name": "The Bleeding Room",
  "theme": "slashers",
  "difficulty": "beginner",
  "questions": [
    {
      "question": "Which masked killer stalked Camp Crystal Lake?",
      "options": ["Michael Myers", "Jason Voorhees", "Freddy Krueger", "Ghostface"],
      "correct": 1
    },
    // ... 4 more questions
  ],
  "score": {
    "current": 0,
    "total": 5,
    "percentage": 0
  },
  "next": {
    "chamber_level": 2,
    "preview": "The Zombie Catacombs"
  }
}
```

**Features:**
- Returns 5 themed questions based on chamber level
- Uses OpenAI to generate dynamic questions (with fallback)
- Cycles through 5 horror chambers: Slashers → Zombies → Vampires → Demons → Cult Horror
- Each chamber has appropriate difficulty scaling

---

### 2. **POST /api/submit_answers**

**Purpose:** Evaluate user answers and return score with progression info.

**Request Body:**
```json
{
  "googleId": "user123" (optional),
  "chamber_level": 1,
  "answers": [1, 0, 2, 1, 3],
  "correct_answers": [1, 2, 2, 1, 0]
}
```

**Response Format:**
```json
{
  "score": {
    "correct": 3,
    "total": 5,
    "percentage": 60.0
  },
  "next": {
    "can_progress": true,
    "chamber_level": 2,
    "chamber_name": "The Zombie Catacombs"
  },
  "result_message": "👹 You escaped... barely.",
  "chamber_completed": true
}
```

**Scoring Logic:**
- 5 correct: "🩸 PERFECT! You've survived this chamber!" → Progress
- 3-4 correct: "👹 You escaped... barely." → Progress
- 2 correct: "🔪 You're bleeding out but alive." → Progress
- 0-1 correct: "💀 The chamber has claimed you. Try again?" → Retry

**Features:**
- Evaluates answers against correct answers
- Determines if user can progress to next chamber
- Saves quiz progress to user profile (if logged in)
- Returns appropriate horror-themed messages

---

## Horror Chambers

The quiz system features 5 progressive chambers:

1. **The Bleeding Room** (Slashers) - Beginner
2. **The Zombie Catacombs** (Zombies) - Intermediate
3. **The Vampire's Lair** (Vampires) - Intermediate
4. **The Demon's Gate** (Demons) - Advanced
5. **The Final Nightmare** (Cult Horror) - Expert

---

## Integration Points

### Backend Changes (horror.py):
- **Line 1137-1229:** `/api/start_quiz` endpoint implementation
- **Line 1231-1335:** `/api/submit_answers` endpoint implementation
- **Line 1337-1378:** `get_fallback_chamber_questions()` helper function
- Integrates with existing `load_user_data()` and `save_user_data()` functions
- Uses OpenAI client if available, falls back to curated question banks

### Key Dependencies:
- Flask, CORS already configured
- OpenAI client (optional - has fallback)
- User data storage (user_data.json)
- Existing datetime, random imports

---

## Testing

### Test /api/start_quiz:
```bash
curl -X POST http://localhost:5000/api/start_quiz \
  -H "Content-Type: application/json" \
  -d '{"chamber_level": 1}'
```

### Test /api/submit_answers:
```bash
curl -X POST http://localhost:5000/api/submit_answers \
  -H "Content-Type: application/json" \
  -d '{
    "chamber_level": 1,
    "answers": [1, 1, 1, 0, 2],
    "correct_answers": [1, 1, 0, 0, 2]
  }'
```

---

## Server Configuration

**Current Port:** 5000 (as configured in horror.py line 1793)
- Frontend API_BASE is set to `http://localhost:5000`
- To change to port 8000, update line 1793: `app.run(host="0.0.0.0", port=8000, debug=True)`
- Also update script-js-combined.js line 13: `const API_BASE = 'http://localhost:8000';`

---

## Error Handling

Both endpoints include comprehensive error handling:
- Invalid JSON → 400 Bad Request
- Missing required fields → 400 with error message
- OpenAI failures → Automatic fallback to curated questions
- User data save failures → Logged but don't break response
- All exceptions caught and returned as JSON with 500 status

---

## Notes

✅ **Validation Complete:** JSON structure matches spec
✅ **Port Configuration:** Currently 5000 (update if needed)
✅ **Backward Compatible:** Doesn't affect existing quiz routes
✅ **Inline Comments:** All changes documented in code
✅ **No Linting Errors:** Code passes validation

The quiz system is now fully functional and ready for frontend integration!

















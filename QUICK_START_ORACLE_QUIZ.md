# Quick Start: Horror Oracle LangGraph Quiz

## 🎯 What Was Fixed

The quiz system now uses **LangChain LLM to generate NEW questions every time** instead of static questions.

## 🔄 Complete Flow

```
┌─────────────────────────────────────────────────────────────┐
│  USER CLICKS "FACE YOUR NIGHTMARES"                         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND: startOracleQuiz()                                │
│  - Calls: POST /api/start_quiz                              │
│  - Sends: { userId: "guest" }                               │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  BACKEND: /api/start_quiz                                   │
│  - Calls: start_first_quiz(userId)                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  LANGGRAPH CHAIN: Start Quiz                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. ProfileNode.get_profile()                         │   │
│  │    → Load user preferences                           │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ 2. BuilderNode.generate_quiz() ⭐                    │   │
│  │    → Calls LangChain LLM (ChatOpenAI)               │   │
│  │    → Temperature: 0.8 for variety                    │   │
│  │    → Generates 5 NEW questions (no cache!)          │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ 3. LoreWhispererNode.generate_lore()                │   │
│  │    → Creates atmospheric intro                       │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ 4. FearMeterNode.translate_to_oracle_state()        │   │
│  │    → Initializes Oracle emotional state             │   │
│  └──────────────────────────────────────────────────────┘   │
│  Returns: { questions, intro, lore, oracle_state }         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND: displayOracleQuiz()                              │
│  - Shows quiz.questions[i].question                         │
│  - Shows quiz.questions[i].choices                          │
│  - Player answers questions                                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  USER SUBMITS ANSWERS                                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND: Submit Answers                                   │
│  - Calls: POST /api/submit_answers                          │
│  - Sends: { userId, quiz, answers }                         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  BACKEND: /api/submit_answers                               │
│  - Calls: evaluate_and_progress(userId, quiz, answers)      │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  LANGGRAPH CHAIN: Evaluate & Progress                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. EvaluatorNode.evaluate_answers()                  │   │
│  │    → Grades performance (score, accuracy)            │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ 2. FearMeterNode.translate_to_oracle_state()         │   │
│  │    → Updates Oracle emotion based on performance     │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ 3. RewardNode.generate_rewards()                     │   │
│  │    → Unlocks content based on score                  │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ 4. ProfileNode.update_profile()                      │   │
│  │    → Saves player stats (bravery, fear_level)        │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ 5. RecommenderNode.recommend_movies()                │   │
│  │    → Suggests horror films based on quiz theme       │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ 6. LoreWhispererNode.whisper_between_chambers()      │   │
│  │    → Generates transition lore                       │   │
│  └──────────────────────────────────────────────────────┘   │
│  Returns: { score, evaluation, oracle_state, rewards,      │
│             recommendations, lore, next_action }            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND: Display Results                                  │
│  - Shows score and Oracle reaction                          │
│  - Shows movie recommendations                              │
│  - Updates fear level meter                                 │
│  - Shows atmospheric transition text                        │
└─────────────────────────────────────────────────────────────┘
```

## 🔑 Key Points

### ✅ BuilderNode Generates NEW Questions Every Time
```python
# oracle_engine/builder_node.py (Line 103-136)

def generate_questions(theme, difficulty, tone):
    print("[BUILDER NODE] Generating NEW questions (no cache)")
    
    # Uses LangChain LLM
    self.llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.8  # High temp = variety!
    )
    
    # Creates chain
    chain = chat_prompt | self.llm | parser
    
    # Invokes LLM - FRESH QUESTIONS EVERY TIME
    result = chain.invoke({theme, difficulty, tone})
    
    return result  # 5 new questions
```

### ✅ No Static Questions (Unless LLM Fails)
The system has fallbacks:
1. **Primary:** LangChain LLM (ChatOpenAI) with temperature 0.8
2. **Fallback:** Direct OpenAI API call with temperature 0.8
3. **Last Resort:** Randomized selection from 100+ static questions

### ✅ Frontend Receives Dynamic Questions
```javascript
// script-js-combined.js (Line 1759-1767)

const quizData = await response.json();

currentQuiz.questions = quizData.questions.map(q => ({
    question: q.question,        // NEW question text
    options: q.choices,          // NEW answer choices
    correct: q.correct_answer,   // Correct answer
    theme: q.theme,              // Horror theme
    difficulty: q.difficulty     // Difficulty level
}));

displayOracleQuiz(quizData);  // Renders quiz
```

## 🧪 How to Test

### 1. Start Backend
```bash
cd C:\31000
python horror.py
```

Look for:
```
[OK] Builder Node: LLM initialized with LangChain
🩸 HORROR ORACLE AWAKENING... 🩸
Server running on http://localhost:5000
```

### 2. Open Frontend
```
http://localhost:5000/index.html
```

### 3. Click "Face Your Nightmares"

### 4. Check Terminal Logs
You should see:
```
[ORACLE ENGINE] Starting quiz for user: guest
[1/4] Loading user profile...
[2/4] Generating quiz questions...
[BUILDER NODE] Generating NEW questions (no cache)
[BUILDER NODE] Theme: general_horror | Difficulty: 0.5 | Tone: creepy
[BUILDER NODE] Calling LLM via LangChain to generate fresh questions...
[BUILDER NODE] Generated 5 NEW questions successfully via LangChain
[BUILDER NODE] Sample Q: In what film does a possessed doll...
[3/4] Whispering lore...
[4/4] Calibrating fear meter...
[OK] Quiz generated | Theme: general_horror | Difficulty: intermediate
```

### 5. Answer Questions & Submit

### 6. Check Evaluation Logs
```
[ORACLE ENGINE] Evaluating answers for user: guest
[1/7] Evaluating answers...
[OK] Score: 4/5 (80.0%)
[2/7] Oracle reacts to performance...
[OK] Oracle Emotion: impressed | Tone: pleased
[3/7] Generating rewards...
[4/7] Updating player profile...
[5/7] Generating movie recommendations...
[6/7] Whispering transition lore...
[7/7] Compiling final state...
[OK] Full chain complete | Next: continue
```

## ⚠️ Troubleshooting

### "No OpenAI API key found"
Add to `.env`:
```
OPENAI_API_KEY=sk-your-key-here
```

### "LangChain import failed"
Install dependencies:
```bash
pip install langchain langchain-openai
```

### Questions Seem Repetitive
- Check logs for "[BUILDER NODE] Calling LLM via LangChain"
- If missing, check OpenAI API key
- Temperature is 0.8 so questions should vary
- Try multiple quizzes to verify different questions

### Frontend Not Displaying Questions
Check browser console for:
```
✅ Questions Generated: 5
📝 First Question: [question text]
```

## 📊 Success Criteria

✅ Every quiz generates **5 NEW questions** via LangChain LLM  
✅ Terminal shows "Calling LLM via LangChain to generate fresh questions"  
✅ Questions vary between quiz attempts (due to temperature 0.8)  
✅ Frontend renders questions dynamically  
✅ Submit answers triggers full evaluation chain  
✅ Oracle reacts emotionally to performance  
✅ Movie recommendations appear based on quiz theme  

## 🎬 Next Steps

1. **Customize Themes:** Modify user profile to test different horror themes (slashers, supernatural, etc.)
2. **Adjust Difficulty:** Change difficulty_level in profile to see how questions adapt
3. **Track Progress:** Complete multiple quizzes to see profile evolution
4. **View Recommendations:** Check movie suggestions after each quiz

---

**Status:** ✅ COMPLETE - Horror Oracle LangGraph backend integration restored!

